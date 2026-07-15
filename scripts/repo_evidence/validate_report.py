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

CITATION_PATTERN = re.compile(
    r"`(?P<path>[^`\n:]+(?:/[^`\n:]+)*):(?P<start>\d+)"
    r"(?:-(?P<end>\d+))?`"
)

MERMAID_PATTERN = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
HEADING_PATTERN = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
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

    report = report_path.read_text(encoding="utf-8")
    headings = set(HEADING_PATTERN.findall(report))
    required_headings = (
        REPOSITORY_HEADINGS if mode == "repository" else PULL_REQUEST_HEADINGS
    )
    errors = []
    warnings = []

    missing_headings = sorted(required_headings - headings)
    if missing_headings:
        errors.append("Missing required sections: " + ", ".join(missing_headings))

    diagrams = MERMAID_PATTERN.findall(report)
    minimum_diagrams = 2 if mode == "repository" else 1
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
    minimum_citations = 5 if mode == "repository" else 3
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

    return mode, diagrams, valid_citations, errors, warnings


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
