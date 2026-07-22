#!/usr/bin/env python3
"""Prepare bounded workflow-specific evidence from one collected snapshot."""

import argparse
import json
from pathlib import Path
import re

from cache_permissions import secure_file
from redact_context import redact_lines

WORKFLOW_CONTEXT_VERSION = 3

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
    "quick": {
        "max_files": 12,
        "max_changed_files": 60,
        "max_chars": 80_000,
        "max_lines": 120,
    },
    "deep": {
        "max_files": 24,
        "max_changed_files": 200,
        "max_chars": 220_000,
        "max_lines": 240,
    },
}

GENERIC_SYMBOL_TOKENS = {
    "application",
    "client",
    "config",
    "controller",
    "dao",
    "dto",
    "entity",
    "handler",
    "impl",
    "model",
    "page",
    "repository",
    "request",
    "response",
    "route",
    "service",
    "test",
}

SENSITIVE_PATH = re.compile(
    r"(^|/)(\.env($|\.)|id_rsa|id_ed25519|credentials?|secrets?)(/|$)|"
    r"\.(pem|p12|pfx|key)$",
    re.IGNORECASE,
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
    secure_file(path)


def symbol_parts(path):
    stem = Path(path).stem
    expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", stem)
    return {
        token.lower()
        for token in re.split(r"[^A-Za-z0-9]+", expanded)
        if len(token) >= 4 and token.lower() not in GENERIC_SYMBOL_TOKENS
    }


def normalized_stem(path):
    return re.sub(r"[^a-z0-9]", "", Path(path).stem.lower())


def rank_evidence(entries, workflow):
    terms = WORKFLOW_PROFILES[workflow]["terms"]
    changed_entries = [
        entry for entry in entries if entry.get("changed_in_pull_request")
    ]
    changed_stems = {
        normalized_stem(entry.get("path", "")) for entry in changed_entries
    }
    changed_stems.discard("")
    changed_tokens = (
        set().union(
            *(symbol_parts(entry.get("path", "")) for entry in changed_entries)
        )
        if changed_entries
        else set()
    )

    def support_score(entry):
        path = entry.get("path", "").lower()
        term_hits = sum(term in path for term in terms)
        normalized_path = re.sub(r"[^a-z0-9]", "", path)
        stem_affinity = sum(stem in normalized_path for stem in changed_stems)
        token_affinity = sum(token in path for token in changed_tokens)
        affinity = (stem_affinity * 10) + token_affinity
        is_relevant = bool(term_hits or affinity)
        return is_relevant, affinity, term_hits, path

    changed_ranked = sorted(
        changed_entries, key=lambda entry: entry.get("path", "").lower()
    )
    supporting = []
    for entry in entries:
        if entry.get("changed_in_pull_request"):
            continue
        relevant, affinity, term_hits, path = support_score(entry)
        if relevant:
            supporting.append((entry, affinity, term_hits, path))
    supporting.sort(key=lambda item: (-item[1], -item[2], item[3]))
    return changed_ranked, [item[0] for item in supporting]


def declared_changed_paths(snapshot, manifest):
    changed_path = snapshot / "pull-request-files.json"
    if changed_path.is_file():
        return sorted(
            {
                item.get("filename")
                for item in read_json(changed_path)
                if item.get("filename")
            }
        )
    return sorted(
        {
            item.get("path")
            for item in manifest.get("collected_files", [])
            if item.get("changed_in_pull_request") and item.get("path")
        }
    )


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


def render_evidence(path, content, terms, max_lines):
    lines = redact_lines(content.splitlines())
    sections = []
    for start, end in citation_windows(lines, terms, max_lines):
        rendered = "\n".join(
            f"{number:>6} | {lines[number - 1]}"
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
    declared_changed = declared_changed_paths(snapshot, manifest)
    declared_changed_set = set(declared_changed)
    entries = []
    for original in manifest.get("collected_files", []):
        entry = dict(original)
        # Validate every manifest path before relevance filtering so an
        # irrelevant-looking traversal entry cannot bypass the safety check.
        resolve_evidence_file(files_root, entry.get("path", ""))
        if entry.get("path") in declared_changed_set:
            entry["changed_in_pull_request"] = True
        entries.append(entry)
    changed_ranked, supporting_ranked = rank_evidence(entries, workflow)
    available_paths = {entry.get("path") for entry in entries}
    available_changed = sorted(declared_changed_set & available_paths)
    missing_changed = sorted(declared_changed_set - available_paths)
    changed_candidates = changed_ranked[: limits["max_changed_files"]]
    supporting_candidates = supporting_ranked[: limits["max_files"]]
    ranked = changed_candidates + supporting_candidates
    selected = []
    skipped_sensitive = []
    blocks = []
    used_chars = 0
    truncated = (
        len(changed_ranked) > limits["max_changed_files"]
        or len(supporting_ranked) > limits["max_files"]
    )

    for entry in ranked:
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
    unavailable_layers = selection.get("unavailable_layers", [])
    if unavailable_layers:
        limitations.append(
            "No candidates were available for evidence layers: "
            + ", ".join(unavailable_layers)
            + "."
        )
    if missing_changed:
        limitations.append(
            f"{len(missing_changed)} declared changed file(s) were not present "
            "in the collected snapshot."
        )
    selected_changed = sorted(declared_changed_set & set(selected))
    unselected_changed = sorted(set(available_changed) - set(selected_changed))
    if unselected_changed:
        limitations.append(
            f"{len(unselected_changed)} collected changed file(s) exceeded the "
            "workflow context budget."
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
        f"- Declared changed files: `{len(declared_changed)}`",
        f"- Changed files present in snapshot: `{len(available_changed)}`",
        f"- Changed files selected: `{len(selected_changed)}`",
        f"- Relevant supporting candidates: `{len(supporting_ranked)}`",
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
    secure_file(output)

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
        "changed_files_total": len(declared_changed),
        "changed_files_available": len(available_changed),
        "changed_files_selected": len(selected_changed),
        "changed_files_missing_from_snapshot": missing_changed,
        "changed_files_unselected": unselected_changed,
        "relevant_supporting_candidates": len(supporting_ranked),
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
