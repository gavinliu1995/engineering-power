#!/usr/bin/env python3
"""Validate RepoLens report structure, diagrams, and source citations."""

import argparse
import json
from pathlib import Path
import re
import sys


REPOSITORY_HEADINGS = {
    "Executive Summary",
    "Repository Map",
    "Architecture Diagram",
    "Business Logic Flows",
    "Developer Onboarding",
    "Build, Test, and Operations",
    "Risks and Recommendations",
    "Evidence Index",
}

PULL_REQUEST_HEADINGS = {
    "Change Summary",
    "Change Propagation",
    "Business Logic Impact",
    "Test Impact",
    "Regression Risk",
    "Architecture Review",
    "Evidence Index",
}

SPECIALIZED_REPORT_HEADINGS = {
    "architecture": {
        "Target and Evidence",
        "System Context and Runtime Units",
        "Module Boundaries and Dependencies",
        "Architecture Diagram",
        "Concrete Feature Flow",
        "Trust, State, and External Boundaries",
        "Risks and Incremental Target State",
        "Unknowns",
        "Evidence Index",
    },
    "dependency-impact": {
        "Decision Summary",
        "Changed or Requested Surface",
        "Dependency Propagation",
        "Transitive Impact",
        "Test Impact",
        "Regression Risks",
        "Evidence Index",
    },
    "api-contract": {
        "Decision Summary",
        "Contract Sources",
        "Operations",
        "Schemas and Validation",
        "Compatibility Findings",
        "Verification",
        "Evidence Index",
    },
    "release-notes": {
        "Decision Summary",
        "User-facing Release Notes",
        "Technical Release Notes",
        "Required Actions",
        "Validation Status",
        "Risks and Compatibility",
        "Evidence Index",
    },
}

REPORT_TYPES = (
    "repository",
    "pull-request",
    *SPECIALIZED_REPORT_HEADINGS,
)

CITATION_PATTERN = re.compile(
    r"`(?P<path>[^`\n:]+(?:/[^`\n:]+)*):(?P<start>\d+)"
    r"(?:-(?P<end>\d+))?`"
)

MERMAID_PATTERN = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
HEADING_PATTERN = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
COVERAGE_PATTERN = re.compile(
    r"^Coverage:\s*(?P<collected>\d+)/(?P<candidates>\d+)\s+text candidates\s*$",
    re.MULTILINE,
)
TREE_ENTRIES_PATTERN = re.compile(
    r"^Tree entries:\s*(?P<count>\d+)\s*$", re.MULTILINE
)
SNAPSHOT_EVIDENCE_FILES = {
    "manifest.json",
    "pull-request-files.json",
    "pull-request.patch",
    "recent-commits.json",
    "tree.txt",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate an evidence-backed RepoLens Markdown report."
    )
    parser.add_argument("report", help="Markdown report path")
    parser.add_argument("--snapshot", required=True, help="Collector snapshot directory")
    parser.add_argument(
        "--report-type",
        choices=REPORT_TYPES,
        help="Report contract; defaults to the repository or pull-request snapshot mode",
    )
    return parser.parse_args()


def line_count(path):
    with path.open("r", encoding="utf-8", errors="replace") as source:
        return sum(1 for _ in source)


def resolve_evidence_path(snapshot, files_root, relative_path):
    if relative_path.startswith("@snapshot/"):
        artifact = relative_path.removeprefix("@snapshot/")
        if artifact not in SNAPSHOT_EVIDENCE_FILES:
            return None, f"Unsupported snapshot evidence file: {artifact}"
        return (snapshot / artifact).resolve(), None
    source_path = (files_root / relative_path).resolve()
    if not str(source_path).startswith(str(files_root) + "/"):
        return None, f"Unsafe evidence path: {relative_path}"
    return source_path, None


def section_body(report, heading):
    match = re.search(
        rf"^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)",
        report,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def require_table_headers(report, heading, required_headers, errors):
    section = section_body(report, heading)
    header_line = next(
        (line for line in section.splitlines() if line.strip().startswith("|")),
        "",
    )
    headers = {
        cell.strip().casefold()
        for cell in header_line.strip().strip("|").split("|")
        if cell.strip()
    }
    missing = [header for header in required_headers if header.casefold() not in headers]
    if missing:
        errors.append(
            f"{heading} table is missing required columns: {', '.join(missing)}"
        )


def require_validation_categories(report, heading, errors):
    section = section_body(report, heading)
    missing = [
        label
        for label in ("Executed", "Discovered", "Recommended")
        if not re.search(rf"\b{label}\b", section, re.IGNORECASE)
    ]
    if missing:
        errors.append(
            f"{heading} must separate executed, discovered, and recommended validation; "
            f"missing: {', '.join(missing)}"
        )


def specialized_contract_errors(report, report_type):
    errors = []
    if report_type == "architecture":
        feature_flow = section_body(report, "Concrete Feature Flow")
        required_stages = (
            ("Page or Route", r"\b(?:Page|Route|Controller|UI)\b"),
            ("Provider or Service", r"\b(?:Provider|Service|Orchestrator)\b"),
            ("Client or DAO", r"\b(?:Client|DAO|Repository|Gateway)\b"),
        )
        missing = [
            label
            for label, pattern in required_stages
            if not re.search(pattern, feature_flow, re.IGNORECASE)
        ]
        if missing or not re.search(r"(?:→|-->|->>)", feature_flow):
            errors.append(
                "Concrete Feature Flow must trace a concrete Page/Route → "
                "Provider/Service → Client/DAO chain; missing: "
                + (", ".join(missing) if missing else "linked direction")
            )
    elif report_type == "dependency-impact":
        require_table_headers(
            report,
            "Dependency Propagation",
            ("Source", "Direction", "Target", "Effect", "Classification", "Evidence"),
            errors,
        )
        propagation = section_body(report, "Dependency Propagation")
        if not re.search(r"\b(?:Fact|Inference|Unknown)\b", propagation):
            errors.append(
                "Dependency Propagation must classify evidence as Fact, Inference, or Unknown"
            )
        require_validation_categories(report, "Test Impact", errors)
    elif report_type == "api-contract":
        require_table_headers(
            report,
            "Operations",
            (
                "Change",
                "Method or kind",
                "Path or name",
                "Input",
                "Output",
                "Authentication",
                "Compatibility",
                "Evidence",
            ),
            errors,
        )
        sources = section_body(report, "Contract Sources")
        if not re.search(r"\b(?:Fact|Inference|Unknown)\b", sources):
            errors.append(
                "Contract Sources must classify evidence as Fact, Inference, or Unknown"
            )
        operations = section_body(report, "Operations")
        if not re.search(
            r"\b(?:added|removed|compatible|potentially breaking|breaking|Unknown)\b",
            operations,
            re.IGNORECASE,
        ):
            errors.append("Operations must include an explicit compatibility classification")
        require_validation_categories(report, "Verification", errors)
    elif report_type == "release-notes":
        require_validation_categories(report, "Validation Status", errors)
    return errors


def coverage_contract_errors(report, manifest):
    stats = manifest.get("stats", {})
    required = ("collected_files", "text_candidates", "tree_entries")
    if not all(isinstance(stats.get(key), int) for key in required):
        return []

    errors = []
    coverage = COVERAGE_PATTERN.search(report)
    if not coverage:
        errors.append(
            "Coverage must use manifest-backed format: "
            "Coverage: COLLECTED/TEXT_CANDIDATES text candidates"
        )
    else:
        actual = (
            int(coverage.group("collected")),
            int(coverage.group("candidates")),
        )
        expected = (stats["collected_files"], stats["text_candidates"])
        if actual != expected:
            errors.append(
                "Coverage disagrees with manifest statistics: "
                f"expected {expected[0]}/{expected[1]} text candidates, "
                f"found {actual[0]}/{actual[1]}"
            )

    tree_entries = TREE_ENTRIES_PATTERN.search(report)
    if not tree_entries:
        errors.append("Report is missing manifest-backed Tree entries metadata")
    elif int(tree_entries.group("count")) != stats["tree_entries"]:
        errors.append(
            "Tree entries disagrees with manifest statistics: "
            f"expected {stats['tree_entries']}, found {tree_entries.group('count')}"
        )
    return errors


def validate(args):
    report_path = Path(args.report).expanduser().resolve()
    snapshot = Path(args.snapshot).expanduser().resolve()
    manifest_path = snapshot / "manifest.json"
    files_root = (snapshot / "files").resolve()

    if not report_path.is_file():
        raise RuntimeError(f"Report not found: {report_path}")
    if not manifest_path.is_file():
        raise RuntimeError(f"Snapshot manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mode = manifest.get("mode")
    if mode not in {"repository", "pull-request"}:
        raise RuntimeError(f"Unsupported snapshot mode: {mode}")

    report_type = getattr(args, "report_type", None) or mode
    if report_type not in REPORT_TYPES:
        raise RuntimeError(f"Unsupported report type: {report_type}")

    report = report_path.read_text(encoding="utf-8")
    headings = set(HEADING_PATTERN.findall(report))
    if report_type == "repository":
        required_headings = REPOSITORY_HEADINGS
    elif report_type == "pull-request":
        required_headings = PULL_REQUEST_HEADINGS
    else:
        required_headings = SPECIALIZED_REPORT_HEADINGS[report_type]
    errors = []
    warnings = []

    errors.extend(coverage_contract_errors(report, manifest))

    missing_headings = sorted(required_headings - headings)
    if missing_headings:
        errors.append("Missing required sections: " + ", ".join(missing_headings))
    if report_type in SPECIALIZED_REPORT_HEADINGS:
        errors.extend(specialized_contract_errors(report, report_type))

    diagrams = MERMAID_PATTERN.findall(report)
    minimum_diagrams = {
        "repository": 2,
        "pull-request": 1,
        "architecture": 2,
    }.get(report_type, 0)
    if len(diagrams) < minimum_diagrams:
        errors.append(
            f"Expected at least {minimum_diagrams} Mermaid diagram(s); found {len(diagrams)}"
        )
    for index, diagram in enumerate(diagrams, start=1):
        first_line = next(
            (line.strip() for line in diagram.splitlines() if line.strip()), ""
        )
        if not re.match(
            r"^(flowchart|graph|sequenceDiagram|stateDiagram|stateDiagram-v2|classDiagram)\b",
            first_line,
        ):
            errors.append(
                f"Mermaid diagram {index} starts with unsupported declaration: {first_line}"
            )
        if "```" in diagram:
            errors.append(f"Mermaid diagram {index} contains a nested code fence")

    citations = list(CITATION_PATTERN.finditer(report))
    minimum_citations = 5 if report_type == "repository" else 3
    valid_citations = 0
    checked_paths = {}
    for citation in citations:
        relative_path = citation.group("path")
        if relative_path.startswith(("http://", "https://")):
            continue
        source_path, path_error = resolve_evidence_path(
            snapshot, files_root, relative_path
        )
        if path_error:
            errors.append(path_error)
            continue
        if not source_path.is_file():
            errors.append(f"Evidence file was not collected: {relative_path}")
            continue
        if source_path not in checked_paths:
            checked_paths[source_path] = line_count(source_path)
        source_lines = checked_paths[source_path]
        start = int(citation.group("start"))
        end = int(citation.group("end") or start)
        if start < 1 or end < start or end > source_lines:
            errors.append(
                f"Evidence range is invalid for {relative_path}: {start}-{end} "
                f"(file has {source_lines} lines)"
            )
            continue
        valid_citations += 1

    if valid_citations < minimum_citations:
        errors.append(
            f"Expected at least {minimum_citations} valid source citations; "
            f"found {valid_citations}"
        )

    resolved_ref = manifest.get("resolved_ref", "")
    if resolved_ref and resolved_ref not in report:
        warnings.append("Report does not mention the analyzed commit SHA")

    if "Confidence:" not in report:
        warnings.append("Report contains no explicit confidence labels")

    return report_type, diagrams, valid_citations, errors, warnings


def main():
    args = parse_args()
    mode, diagrams, citations, errors, warnings = validate(args)
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for report_error in errors:
            print(f"ERROR: {report_error}", file=sys.stderr)
        return 1
    print(
        f"RepoLens report is valid: mode={mode}, diagrams={len(diagrams)}, "
        f"citations={citations}"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        sys.exit(1)
