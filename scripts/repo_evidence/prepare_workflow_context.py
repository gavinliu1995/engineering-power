#!/usr/bin/env python3
"""Prepare bounded workflow-specific evidence from one collected snapshot."""

import argparse
import json
from pathlib import Path
import re


WORKFLOW_CONTEXT_VERSION = 1

WORKFLOW_PROFILES = {
    "dependency-impact": {
        "terms": (
            "dependency",
            "dependencies",
            "pom.xml",
            "build.gradle",
            "package.json",
            "requirements",
            "import",
            "client",
        ),
    },
    "api-contract": {
        "terms": (
            "controller",
            "route",
            "endpoint",
            "openapi",
            "swagger",
            "schema",
            "dto",
            "request",
            "response",
            "graphql",
            "protobuf",
        ),
    },
    "release-notes": {
        "terms": (
            "changelog",
            "release",
            "readme",
            "controller",
            "route",
            "service",
            "config",
            "deploy",
            "migration",
            "test",
        ),
    },
}

PROFILE_LIMITS = {
    "quick": {"max_files": 12, "max_chars": 80_000, "max_lines": 120},
    "deep": {"max_files": 24, "max_chars": 220_000, "max_lines": 240},
}

SENSITIVE_PATH = re.compile(
    r"(^|/)(\.env($|\.)|id_rsa|id_ed25519|credentials?|secrets?)(/|$)|"
    r"\.(pem|p12|pfx|key)$",
    re.IGNORECASE,
)
SENSITIVE_ASSIGNMENT = re.compile(
    r"(?i)(password|passwd|secret|token|api[_-]?key|private[_-]?key)"
    r"(\s*[=:]\s*)([^\s,;]+)"
)


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"Could not read JSON file {path}: {exc}") from exc


def write_json(path, value):
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def rank_evidence(entries, workflow):
    terms = WORKFLOW_PROFILES[workflow]["terms"]

    def score(entry):
        path = entry.get("path", "").lower()
        term_hits = sum(term in path for term in terms)
        changed = bool(entry.get("changed_in_pull_request"))
        return (-int(changed), -term_hits, path)

    return sorted(entries, key=score)


def citation_windows(lines, terms, max_lines):
    if not lines:
        return []
    if len(lines) <= max_lines:
        return [(1, len(lines))]

    hits = []
    lowered_terms = tuple(term.lower() for term in terms)
    for number, line in enumerate(lines, start=1):
        lowered = line.lower()
        if any(term in lowered for term in lowered_terms):
            hits.append(number)

    raw = [(1, min(25, len(lines)))]
    raw.extend((max(1, hit - 4), min(len(lines), hit + 8)) for hit in hits[:24])
    merged = []
    for start, end in sorted(raw):
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    bounded = []
    used = 0
    for start, end in merged:
        if used >= max_lines:
            break
        bounded_end = min(end, start + max_lines - used - 1)
        bounded.append((start, bounded_end))
        used += bounded_end - start + 1
    return bounded


def resolve_evidence_file(files_root, relative_path):
    candidate = (files_root / relative_path).resolve()
    try:
        candidate.relative_to(files_root.resolve())
    except ValueError as exc:
        raise RuntimeError(
            f"Evidence path is outside snapshot files: {relative_path}"
        ) from exc
    return candidate


def redact_line(line):
    return SENSITIVE_ASSIGNMENT.sub(r"\1\2[REDACTED]", line)


def render_evidence(path, content, terms, max_lines):
    lines = content.splitlines()
    sections = []
    for start, end in citation_windows(lines, terms, max_lines):
        rendered = "\n".join(
            f"{number:>6} | {redact_line(lines[number - 1])}"
            for number in range(start, end + 1)
        )
        sections.extend(
            [
                f"### {path}:L{start}-L{end}",
                "",
                "```text",
                rendered,
                "```",
                "",
            ]
        )
    return "\n".join(sections)


def build_workflow_context(snapshot, workflow, profile, output):
    snapshot = Path(snapshot).expanduser().resolve()
    output = Path(output).expanduser().resolve()
    if workflow not in WORKFLOW_PROFILES:
        raise ValueError(f"Unsupported workflow: {workflow}")
    if profile not in PROFILE_LIMITS:
        raise ValueError(f"Unsupported profile: {profile}")

    manifest_path = snapshot / "manifest.json"
    files_root = snapshot / "files"
    if not manifest_path.is_file() or not files_root.is_dir():
        raise RuntimeError(f"Invalid evidence snapshot: {snapshot}")

    manifest = read_json(manifest_path)
    limits = PROFILE_LIMITS[profile]
    terms = WORKFLOW_PROFILES[workflow]["terms"]
    ranked = rank_evidence(manifest.get("collected_files", []), workflow)
    selected = []
    skipped_sensitive = []
    blocks = []
    used_chars = 0
    truncated = len(ranked) > limits["max_files"]

    for entry in ranked:
        if len(selected) >= limits["max_files"]:
            break
        relative_path = entry.get("path", "")
        source = resolve_evidence_file(files_root, relative_path)
        if SENSITIVE_PATH.search(relative_path):
            skipped_sensitive.append(relative_path)
            continue
        if not source.is_file():
            continue
        content = source.read_text(encoding="utf-8", errors="replace")
        block = render_evidence(
            relative_path, content, terms, limits["max_lines"]
        )
        if not block:
            continue
        if used_chars + len(block) > limits["max_chars"]:
            truncated = True
            break
        blocks.append(block)
        selected.append(relative_path)
        used_chars += len(block)

    selection = manifest.get("selection", {})
    limitations = []
    if selection.get("deadline_reached"):
        limitations.append("Evidence collection reached its deadline.")
    if selection.get("missing_layers"):
        limitations.append(
            "Missing evidence layers: " + ", ".join(selection["missing_layers"]) + "."
        )
    if truncated:
        limitations.append("Workflow context reached its profile budget.")
    if skipped_sensitive:
        limitations.append("Sensitive-path evidence was excluded.")
    if not limitations:
        limitations.append("No collector or workflow-context limitation was recorded.")

    lines = [
        f"# Engineering Power {workflow} Context",
        "",
        "> Bounded evidence for one workflow. This is not the final report.",
        "",
        "## Snapshot",
        "",
        f"- Workflow: `{workflow}`",
        f"- Profile: `{profile}`",
        f"- Mode: `{manifest.get('mode')}`",
        f"- Target: `{manifest.get('target_url')}`",
        f"- Resolved commit: `{manifest.get('resolved_ref')}`",
        f"- Authentication: `{manifest.get('authentication', {}).get('method')}`",
        f"- Context policy: `{WORKFLOW_CONTEXT_VERSION}`",
        "",
        "## Selected Evidence",
        "",
        *blocks,
        "## Coverage Limitations",
        "",
        *(f"- {item}" for item in limitations),
        "",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")

    result = {
        "context": str(output),
        "workflow_context_version": WORKFLOW_CONTEXT_VERSION,
        "workflow": workflow,
        "profile": profile,
        "mode": manifest.get("mode"),
        "target": manifest.get("target_url"),
        "resolved_ref": manifest.get("resolved_ref"),
        "selected_files": selected,
        "selected_file_count": len(selected),
        "truncated": truncated,
        "skipped_sensitive_files": skipped_sensitive,
        "limitations": limitations,
    }
    write_json(output.with_suffix(".json"), result)
    return result


def parse_args():
    parser = argparse.ArgumentParser(
        description="Prepare bounded workflow evidence from one collected snapshot."
    )
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--workflow", choices=sorted(WORKFLOW_PROFILES), required=True)
    parser.add_argument("--profile", choices=sorted(PROFILE_LIMITS), default="quick")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main():
    args = parse_args()
    output = args.output or (
        args.snapshot / f"workflow-context-{args.workflow}-{args.profile}.md"
    )
    result = build_workflow_context(
        args.snapshot, args.workflow, args.profile, output
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
