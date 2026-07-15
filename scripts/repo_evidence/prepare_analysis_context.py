#!/usr/bin/env python3
"""Build one bounded, citation-ready evidence document from a RepoLens snapshot."""

import argparse
import json
from pathlib import Path
import re
import sys
import time

from collect_github_context import LAYER_ORDER, progress, select_candidates


CONTEXT_POLICY_VERSION = 4

CONTEXT_DEFAULTS = {
    "quick": {
        "max_files": 32,
        "max_chars": 240_000,
        "max_lines_per_file": 150,
        "deadline_seconds": 20,
    },
    "deep": {
        "max_files": 64,
        "max_chars": 650_000,
        "max_lines_per_file": 280,
        "deadline_seconds": 60,
    },
}

INTERESTING = re.compile(
    r"(^|\W)(class|interface|record|enum|def|func|function|route|controller|service|"
    r"repository|dao|handler|endpoint|schedule|transaction|authorize|validate|save|"
    r"create|update|delete|execute|process|main|bootstrap|application)(\W|$)",
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


def metadata_path(output):
    return output.with_suffix(".json")


def merge_windows(windows, line_count, limit):
    normalized = []
    for start, end in sorted(windows):
        start = max(1, start)
        end = min(line_count, end)
        if start > end:
            continue
        if normalized and start <= normalized[-1][1] + 2:
            normalized[-1] = (normalized[-1][0], max(normalized[-1][1], end))
        else:
            normalized.append((start, end))

    result = []
    used = 0
    for start, end in normalized:
        if used >= limit:
            break
        allowed_end = min(end, start + (limit - used) - 1)
        result.append((start, allowed_end))
        used += allowed_end - start + 1
    return result


def excerpt_windows(lines, max_lines):
    if len(lines) <= max_lines:
        return [(1, len(lines))] if lines else []
    windows = [(1, min(55, len(lines)))]
    hits = [
        index
        for index, line in enumerate(lines, start=1)
        if INTERESTING.search(line)
    ]
    for line_number in hits[:30]:
        windows.append((line_number - 5, line_number + 12))
    return merge_windows(windows, len(lines), max_lines)


def top_level_summary(tree_path):
    counts = {}
    if not tree_path.is_file():
        return counts
    for line in tree_path.read_text(encoding="utf-8", errors="replace").splitlines():
        fields = line.split("\t", 2)
        if len(fields) != 3:
            continue
        repository_path = fields[2]
        top = repository_path.split("/", 1)[0]
        counts[top] = counts.get(top, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:25])


def selected_evidence(manifest, profile):
    defaults = CONTEXT_DEFAULTS[profile]
    files = [
        {
            "path": item["path"],
            "size": item.get("size", 0),
            "sha": item.get("sha"),
            "layer": item.get("layer", "other"),
        }
        for item in manifest.get("collected_files", [])
    ]
    changed = {
        item["path"]
        for item in manifest.get("collected_files", [])
        if item.get("changed_in_pull_request")
    }
    selected, _ = select_candidates(
        files,
        changed,
        defaults["max_files"],
        defaults["max_chars"],
    )
    return selected


def reasoning_anchors(selected):
    """Return a compact, layer-balanced map of named analysis starting points."""
    per_layer_limit = {
        "core": 3,
        "entrypoint": 2,
        "route": 3,
        "service": 3,
        "persistence": 2,
        "test": 2,
        "operations": 2,
        "other": 1,
    }
    source_suffixes = {
        ".c", ".cs", ".go", ".java", ".js", ".jsx", ".kt", ".php",
        ".py", ".rb", ".rs", ".scala", ".swift", ".ts", ".tsx",
    }

    def anchor_priority(entry):
        path = Path(entry["path"])
        if path.suffix.lower() in source_suffixes:
            return (0, entry["path"])
        return (1, entry["path"])

    grouped = {layer: [] for layer in LAYER_ORDER}
    for entry in sorted(selected, key=anchor_priority):
        layer = entry.get("layer", "other")
        if layer in grouped and len(grouped[layer]) < per_layer_limit[layer]:
            grouped[layer].append(entry["path"])
    return {
        layer: paths
        for layer, paths in grouped.items()
        if paths
    }


def build_context(snapshot, profile, output, deadline_seconds):
    started_at = time.monotonic()
    manifest_path = snapshot / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"RepoLens manifest not found: {manifest_path}")
    manifest = read_json(manifest_path)
    files_root = snapshot / "files"
    if not files_root.is_dir():
        raise RuntimeError(f"RepoLens files directory not found: {files_root}")

    progress(profile, 1, 3, "Reading manifest and coverage metadata")
    selected = selected_evidence(manifest, profile)
    defaults = CONTEXT_DEFAULTS[profile]
    selection = manifest.get("selection", {})
    warnings = list(manifest.get("warnings", []))
    limitations = []
    if selection.get("deadline_reached"):
        limitations.append("Evidence collection reached its hard deadline.")
    if selection.get("truncated_by_file_limit"):
        limitations.append("Repository candidates exceeded the profile file budget.")
    if selection.get("truncated_by_byte_limit"):
        limitations.append("Repository candidates exceeded the profile byte budget.")
    if selection.get("missing_layers"):
        limitations.append(
            "No selected evidence was available for layers: "
            + ", ".join(selection["missing_layers"])
            + "."
        )

    lines = [
        "# RepoLens Analysis Context",
        "",
        "> This is a bounded evidence bundle, not the final report. Citations below",
        "> refer to original repository-relative paths and line numbers.",
        "",
        "## Snapshot",
        "",
        f"- Profile: `{profile}`",
        f"- Context policy: `{CONTEXT_POLICY_VERSION}`",
        f"- Mode: `{manifest.get('mode')}`",
        f"- Target: `{manifest.get('target_url')}`",
        f"- Resolved commit: `{manifest.get('resolved_ref')}`",
        f"- Authentication: `{manifest.get('authentication', {}).get('method')}`",
        f"- Collected files: `{manifest.get('stats', {}).get('collected_files', 0)}`",
        f"- Collected bytes: `{manifest.get('stats', {}).get('collected_bytes', 0)}`",
        "",
        "## Layer Coverage",
        "",
        "| Layer | Candidates | Collected |",
        "|---|---:|---:|",
    ]
    candidates = selection.get("layer_candidates", {})
    collected = selection.get("layer_selected", {})
    for layer in LAYER_ORDER:
        lines.append(
            f"| {layer} | {candidates.get(layer, 0)} | {collected.get(layer, 0)} |"
        )

    lines.extend(
        [
            "",
            "## Reasoning Anchors",
            "",
            "Use these named, layer-balanced starting points to make the report",
            "repository-specific. Paths are navigation aids, not proof: cite the",
            "line-numbered excerpts below for every material claim.",
            "",
            "| Layer | Representative selected files |",
            "|---|---|",
        ]
    )
    for layer, paths in reasoning_anchors(selected).items():
        rendered_paths = "; ".join(f"`{path}`" for path in paths)
        lines.append(f"| {layer} | {rendered_paths} |")

    summary = top_level_summary(snapshot / "tree.txt")
    lines.extend(["", "## Top-level Repository Shape", ""])
    for name, count in summary.items():
        lines.append(f"- `{name}`: {count} tree entries")

    if manifest.get("pull_request"):
        pull = manifest["pull_request"]
        lines.extend(
            [
                "",
                "## Change Scope",
                "",
                f"- Base: `{pull.get('base_ref')}` / `{pull.get('base_sha')}`",
                f"- Head: `{pull.get('head_ref')}` / `{pull.get('head_sha')}`",
                f"- Changed files: `{pull.get('changed_files')}`",
            ]
        )
        changed_path = snapshot / "pull-request-files.json"
        if changed_path.is_file():
            for item in read_json(changed_path)[:100]:
                lines.append(f"- `{item.get('status')}` `{item.get('filename')}`")

    progress(profile, 2, 3, "Extracting citation-ready evidence in one pass")
    lines.extend(["", "## Citation-ready Evidence", ""])
    included = []
    context_truncated = False
    for entry in selected:
        if time.monotonic() - started_at >= deadline_seconds:
            limitations.append(
                f"Context extraction stopped at its {deadline_seconds}s deadline."
            )
            break
        source = (files_root / entry["path"]).resolve()
        if not str(source).startswith(str(files_root.resolve()) + "/"):
            continue
        try:
            source_lines = source.read_text(
                encoding="utf-8", errors="replace"
            ).splitlines()
        except OSError:
            continue
        windows = excerpt_windows(source_lines, defaults["max_lines_per_file"])
        if not windows:
            continue
        section = [f"### `{entry['path']}`", ""]
        for start, end in windows:
            section.append(f"Citation: `{entry['path']}:{start}-{end}`")
            section.append("```text")
            for number in range(start, end + 1):
                section.append(f"{number:>6} | {source_lines[number - 1]}")
            section.extend(["```", ""])
        prospective = "\n".join(lines + section)
        if len(prospective) > defaults["max_chars"]:
            context_truncated = True
            break
        lines.extend(section)
        included.append(entry["path"])

    if context_truncated:
        limitations.append("Citation context reached the profile character budget.")
    lines.extend(["", "## Coverage Limits", ""])
    if warnings:
        for warning in warnings:
            lines.append(f"- Collector warning: {warning}")
    if limitations:
        for limitation in limitations:
            lines.append(f"- {limitation}")
    if not warnings and not limitations:
        lines.append("- No collector truncation or deadline limitation was recorded.")
    lines.extend(
        [
            "",
            f"Evidence files included here: {len(included)} of {len(selected)} selected.",
            "Use `tree.txt` and the manifest only to identify explicitly disclosed gaps;",
            "do not start a second Quick collection.",
            "",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    progress(profile, 3, 3, "Citation-ready context complete")
    return {
        "context": str(output.resolve()),
        "context_policy_version": CONTEXT_POLICY_VERSION,
        "profile": profile,
        "files_included": len(included),
        "files_selected": len(selected),
        "text_candidates": manifest.get("stats", {}).get("text_candidates", 0),
        "collected_files": manifest.get("stats", {}).get("collected_files", 0),
        "layer_coverage": collected,
        "missing_layers": selection.get("missing_layers", []),
        "elapsed_seconds": round(time.monotonic() - started_at, 3),
        "limitations": limitations,
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create one bounded analysis context from a RepoLens snapshot."
    )
    parser.add_argument("snapshot", help="RepoLens snapshot directory")
    parser.add_argument("--profile", choices=sorted(CONTEXT_DEFAULTS))
    parser.add_argument("--output", help="Context Markdown path")
    parser.add_argument("--deadline-seconds", type=int)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    snapshot = Path(args.snapshot).expanduser().resolve()
    manifest = read_json(snapshot / "manifest.json")
    profile = args.profile or manifest.get("profile", "quick")
    defaults = CONTEXT_DEFAULTS[profile]
    deadline = args.deadline_seconds or defaults["deadline_seconds"]
    output = (
        Path(args.output).expanduser()
        if args.output
        else snapshot / f"analysis-context-{profile}.md"
    )
    cache_marker = f"- Context policy: `{CONTEXT_POLICY_VERSION}`"
    sidecar = metadata_path(output)
    cache_valid = False
    cached_metadata = None
    if output.exists() and sidecar.is_file() and not args.force:
        try:
            cached_metadata = read_json(sidecar)
            cache_valid = (
                cache_marker
                in output.read_text(encoding="utf-8", errors="replace")[:4000]
                and cached_metadata.get("context_policy_version")
                == CONTEXT_POLICY_VERSION
            )
        except (OSError, RuntimeError):
            cache_valid = False
    if cache_valid:
        result = dict(cached_metadata)
        result["cache_hit"] = True
        result["elapsed_seconds"] = 0
        print(
            json.dumps(result, ensure_ascii=False)
        )
        return
    result = build_context(snapshot, profile, output, deadline)
    result["cache_hit"] = False
    write_json(sidecar, result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        print(f"Context preparation failed: {exc}", file=sys.stderr)
        sys.exit(1)
