#!/usr/bin/env python3
"""Validate and finalize an inline RepoLens report with runtime metadata."""

import argparse
import json
from pathlib import Path
import re
import sys
import time
from types import SimpleNamespace

import validate_report


VALIDATION_PLACEHOLDER = "{{REPOLENS_VALIDATION_STATUS}}"
ELAPSED_PLACEHOLDER = "{{REPOLENS_TOTAL_ELAPSED}}"

PROFILE_RULES = {
    "quick": {"max_chars": 10_000, "deadline_seconds": 120},
    "deep": {"max_chars": 35_000, "deadline_seconds": 300},
}

REQUIRED_METADATA = (
    "Profile:",
    "Collection:",
    "Coverage:",
    "Missing layers:",
    "Tests executed:",
    "Report validation:",
    "Total elapsed:",
)


def section_body(report, heading):
    match = re.search(
        rf"^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)",
        report,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def list_item_count(section):
    return len(re.findall(r"^\s*(?:[-*]|\d+\.)\s+", section, re.MULTILINE))


def profile_errors(report, profile, mode=None):
    errors = []
    expected_profile = profile.title()
    if not re.search(
        rf"^Profile:\s*{re.escape(expected_profile)}\s*$", report, re.MULTILINE
    ):
        errors.append(f"Report metadata must contain: Profile: {expected_profile}")
    for label in REQUIRED_METADATA:
        if not re.search(rf"^{re.escape(label)}", report, re.MULTILINE):
            errors.append(f"Report metadata is missing: {label}")
    if report.count(VALIDATION_PLACEHOLDER) != 1:
        errors.append(
            "Report must contain exactly one validation placeholder: "
            + VALIDATION_PLACEHOLDER
        )
    if report.count(ELAPSED_PLACEHOLDER) != 1:
        errors.append(
            "Report must contain exactly one elapsed-time placeholder: "
            + ELAPSED_PLACEHOLDER
        )
    max_chars = PROFILE_RULES[profile]["max_chars"]
    if len(report) > max_chars:
        errors.append(
            f"{profile.title()} report exceeds {max_chars} characters: {len(report)}"
        )
    if profile == "quick" and mode == "repository":
        architecture = section_body(report, "Architecture Diagram")
        business = section_body(report, "Business Logic Flows")
        if len(validate_report.MERMAID_PATTERN.findall(architecture)) != 1:
            errors.append("Quick repository report requires one architecture diagram")
        if len(validate_report.MERMAID_PATTERN.findall(business)) != 1:
            errors.append("Quick repository report requires one business-flow diagram")
        evidence_items = list_item_count(section_body(report, "Evidence Index"))
        if not 8 <= evidence_items <= 12:
            errors.append(
                "Quick repository Evidence Index requires 8-12 list items; "
                f"found {evidence_items}"
            )
        risk_items = list_item_count(
            section_body(report, "Risks and Recommendations")
        )
        if not 1 <= risk_items <= 5:
            errors.append(
                "Quick repository report requires 1-5 prioritized risks; "
                f"found {risk_items}"
            )
    return errors


def finalize(draft, snapshot, profile, started_at_epoch, output):
    if started_at_epoch <= 0:
        raise RuntimeError("--started-at-epoch must be greater than zero")
    report = draft.read_text(encoding="utf-8")
    mode, diagrams, citations, errors, warnings = validate_report.validate(
        SimpleNamespace(report=str(draft), snapshot=str(snapshot))
    )
    errors.extend(profile_errors(report, profile, mode))
    if errors:
        raise RuntimeError("; ".join(errors))

    elapsed_seconds = max(0.0, time.time() - started_at_epoch)
    deadline_seconds = PROFILE_RULES[profile]["deadline_seconds"]
    deadline_exceeded = elapsed_seconds > deadline_seconds
    elapsed_text = f"{elapsed_seconds:.1f} seconds"
    if deadline_exceeded:
        elapsed_text += " (deadline exceeded)"

    finalized = report.replace(VALIDATION_PLACEHOLDER, "passed").replace(
        ELAPSED_PLACEHOLDER, elapsed_text
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(finalized, encoding="utf-8")

    final_mode, final_diagrams, final_citations, final_errors, final_warnings = (
        validate_report.validate(
            SimpleNamespace(report=str(output), snapshot=str(snapshot))
        )
    )
    if final_errors:
        output.unlink(missing_ok=True)
        raise RuntimeError("Final report validation failed: " + "; ".join(final_errors))

    return {
        "report": str(output.resolve()),
        "profile": profile,
        "validation": "passed",
        "mode": final_mode,
        "diagrams": len(final_diagrams),
        "citations": final_citations,
        "report_characters": len(finalized),
        "total_elapsed_seconds": round(elapsed_seconds, 3),
        "deadline_seconds": deadline_seconds,
        "deadline_exceeded": deadline_exceeded,
        "warnings": sorted(set(warnings + final_warnings)),
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate and finalize a RepoLens report for inline delivery."
    )
    parser.add_argument("draft", help="Draft Markdown report with RepoLens placeholders")
    parser.add_argument("--snapshot", required=True, help="Collector snapshot directory")
    parser.add_argument("--profile", choices=sorted(PROFILE_RULES), required=True)
    parser.add_argument("--started-at-epoch", type=float, required=True)
    parser.add_argument("--output", help="Final Markdown path; defaults to replacing draft")
    return parser.parse_args()


def main():
    args = parse_args()
    draft = Path(args.draft).expanduser().resolve()
    snapshot = Path(args.snapshot).expanduser().resolve()
    output = (
        Path(args.output).expanduser().resolve()
        if args.output
        else draft
    )
    result = finalize(
        draft, snapshot, args.profile, args.started_at_epoch, output
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Report finalization failed: {exc}", file=sys.stderr)
        sys.exit(1)
