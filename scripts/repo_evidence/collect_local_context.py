#!/usr/bin/env python3
"""Collect a bounded RepoLens evidence snapshot from a local Git repository."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time
from urllib import parse

from collect_github_context import (
    PROFILE_DEFAULTS,
    SELECTION_POLICY_VERSION,
    apply_profile,
    cache_manifest_result,
    collection_fingerprint,
    find_cached_snapshot,
    is_text_candidate,
    progress,
    select_candidates,
    write_json,
)


def run_git(repository, arguments, check=True):
    result = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            f"Git command failed: git {' '.join(arguments)}: {detail}"
        )
    return result


def repository_root(path):
    candidate = Path(path).expanduser()
    if not candidate.is_dir():
        raise RuntimeError(f"Local repository directory not found: {candidate}")
    result = run_git(candidate, ["rev-parse", "--show-toplevel"])
    root = Path(result.stdout.decode("utf-8", errors="replace").strip()).resolve()
    if not root.is_dir():
        raise RuntimeError(f"Git repository root is unavailable: {root}")
    return root


def resolve_commit(repository, reference):
    result = run_git(
        repository, ["rev-parse", "--verify", f"{reference}^{{commit}}"]
    )
    return result.stdout.decode("ascii", errors="replace").strip()


def default_branch(repository):
    remote_head = run_git(
        repository,
        ["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"],
        check=False,
    )
    if remote_head.returncode == 0:
        value = remote_head.stdout.decode("utf-8", errors="replace").strip()
        return value.removeprefix("origin/")
    for candidate in ("main", "master"):
        if run_git(
            repository,
            ["rev-parse", "--verify", f"{candidate}^{{commit}}"],
            check=False,
        ).returncode == 0:
            return candidate
    return "HEAD"


def sanitize_remote(remote):
    if not remote:
        return None
    if "://" not in remote:
        return remote
    parts = parse.urlsplit(remote)
    host = parts.hostname or ""
    if parts.port:
        host = f"{host}:{parts.port}"
    return parse.urlunsplit((parts.scheme, host, parts.path, "", ""))


def remote_origin(repository):
    result = run_git(repository, ["remote", "get-url", "origin"], check=False)
    if result.returncode != 0:
        return None
    return sanitize_remote(
        result.stdout.decode("utf-8", errors="replace").strip()
    )


def commit_tree(repository, commit):
    result = run_git(repository, ["ls-tree", "-r", "-l", "-z", commit])
    entries = []
    for record in result.stdout.split(b"\0"):
        if not record or b"\t" not in record:
            continue
        header, raw_path = record.split(b"\t", 1)
        fields = header.decode("ascii", errors="replace").split()
        if len(fields) != 4:
            continue
        mode, object_type, object_id, raw_size = fields
        if object_type != "blob":
            continue
        entries.append(
            {
                "mode": mode,
                "type": object_type,
                "sha": object_id,
                "size": None if raw_size == "-" else int(raw_size),
                "path": raw_path.decode("utf-8", errors="replace"),
                "source": "git-object",
            }
        )
    return entries


def worktree_files(repository):
    result = run_git(
        repository, ["ls-files", "-c", "-o", "--exclude-standard", "-z"]
    )
    entries = []
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        path = raw_path.decode("utf-8", errors="replace")
        source = repository / path
        try:
            metadata = source.lstat()
        except OSError:
            continue
        if source.is_symlink() or not source.is_file():
            continue
        entries.append(
            {
                "mode": oct(metadata.st_mode),
                "type": "blob",
                "sha": None,
                "size": metadata.st_size,
                "path": path,
                "source": "working-tree",
            }
        )
    return entries


def recent_commits(repository, reference):
    result = run_git(
        repository,
        [
            "log",
            "-20",
            "--date=iso-strict",
            "--format=%H%x1f%an%x1f%aI%x1f%s%x1e",
            reference,
        ],
    )
    commits = []
    text = result.stdout.decode("utf-8", errors="replace")
    for record in text.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        fields = record.split("\x1f", 3)
        if len(fields) != 4:
            continue
        sha, author, authored_at, subject = fields
        commits.append(
            {
                "sha": sha,
                "message": subject,
                "author_name": author,
                "author_date": authored_at,
                "author_login": None,
            }
        )
    return commits


def parse_name_status(raw):
    values = [item for item in raw.split(b"\0") if item]
    changed = []
    index = 0
    while index < len(values):
        status = values[index].decode("utf-8", errors="replace")
        index += 1
        if "\t" in status:
            status, path = status.split("\t", 1)
        else:
            if index >= len(values):
                break
            path = values[index].decode("utf-8", errors="replace")
            index += 1
        item = {
            "filename": path,
            "status": status,
            "previous_filename": None,
        }
        if status.startswith(("R", "C")) and index < len(values):
            item["previous_filename"] = path
            item["filename"] = values[index].decode(
                "utf-8", errors="replace"
            )
            index += 1
        changed.append(item)
    return changed


def git_range_diff(repository, base_commit, head_commit):
    merge_base = run_git(
        repository, ["merge-base", base_commit, head_commit]
    ).stdout.decode("ascii", errors="replace").strip()
    patch = run_git(
        repository,
        [
            "diff",
            "--find-renames",
            "--no-ext-diff",
            "--no-color",
            "--unified=80",
            merge_base,
            head_commit,
            "--",
        ],
    ).stdout
    status = run_git(
        repository,
        ["diff", "--name-status", "-z", "--find-renames", merge_base, head_commit],
    ).stdout
    return merge_base, patch, parse_name_status(status)


def untracked_paths(repository):
    result = run_git(
        repository, ["ls-files", "--others", "--exclude-standard", "-z"]
    )
    return [
        item.decode("utf-8", errors="replace")
        for item in result.stdout.split(b"\0")
        if item
    ]


def working_tree_diff(repository, base_commit):
    patch = run_git(
        repository,
        [
            "diff",
            "--find-renames",
            "--no-ext-diff",
            "--no-color",
            "--unified=80",
            base_commit,
            "--",
        ],
    ).stdout
    status = run_git(
        repository,
        ["diff", "--name-status", "-z", "--find-renames", base_commit, "--"],
    ).stdout
    changed = parse_name_status(status)
    known_paths = {item["filename"] for item in changed}
    patch_parts = [patch]
    for path in untracked_paths(repository):
        if path not in known_paths:
            changed.append(
                {"filename": path, "status": "A", "previous_filename": None}
            )
        result = run_git(
            repository,
            [
                "diff",
                "--no-index",
                "--no-color",
                "--unified=80",
                "--",
                "/dev/null",
                path,
            ],
            check=False,
        )
        if result.returncode not in {0, 1}:
            detail = result.stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"Could not diff untracked file {path}: {detail}")
        patch_parts.append(result.stdout)
    return b"\n".join(part for part in patch_parts if part), changed


def strip_patch_prefix(path):
    if path == "/dev/null":
        return path
    return path[2:] if path.startswith(("a/", "b/")) else path


def parse_patch(patch_text):
    blocks = re.split(r"(?=^diff --git )", patch_text, flags=re.MULTILINE)
    changed = []
    for block in blocks:
        if not block.startswith("diff --git "):
            continue
        header = block.splitlines()[0]
        try:
            fields = shlex.split(header)
        except ValueError:
            continue
        if len(fields) < 4:
            continue
        old_path = strip_patch_prefix(fields[2])
        new_path = strip_patch_prefix(fields[3])
        status = "M"
        if "\nnew file mode " in block:
            status = "A"
        elif "\ndeleted file mode " in block:
            status = "D"
        elif "\nrename from " in block and "\nrename to " in block:
            status = "R"
        filename = old_path if new_path == "/dev/null" else new_path
        changed.append(
            {
                "filename": filename,
                "status": status,
                "previous_filename": old_path if status == "R" else None,
            }
        )
    if changed:
        return changed

    # Some exported patches omit the `diff --git` header. Fall back to the
    # standard unified-diff file headers so an offline download remains useful.
    lines = patch_text.splitlines()
    index = 0
    while index + 1 < len(lines):
        if not lines[index].startswith("--- ") or not lines[index + 1].startswith(
            "+++ "
        ):
            index += 1
            continue
        old_path = strip_patch_prefix(lines[index][4:].split("\t", 1)[0])
        new_path = strip_patch_prefix(lines[index + 1][4:].split("\t", 1)[0])
        status = "M"
        if old_path == "/dev/null":
            status = "A"
        elif new_path == "/dev/null":
            status = "D"
        filename = old_path if new_path == "/dev/null" else new_path
        if filename and filename != "/dev/null":
            changed.append(
                {
                    "filename": filename,
                    "status": status,
                    "previous_filename": None,
                }
            )
        index += 2
    return changed


def decode_text_blob(raw):
    if b"\x00" in raw:
        raise RuntimeError("Blob appears to be binary")
    raw.decode("utf-8")
    return raw


def read_entry(repository, entry):
    if entry["source"] == "git-object":
        raw = run_git(repository, ["cat-file", "blob", entry["sha"]]).stdout
    else:
        source = (repository / entry["path"]).resolve()
        if not str(source).startswith(str(repository) + os.sep):
            raise RuntimeError("Unsafe working-tree path")
        if source.is_symlink():
            raise RuntimeError("Refusing to read a symbolic link")
        raw = source.read_bytes()
    return decode_text_blob(raw)


def safe_repository_metadata(repository, reference):
    branch_result = run_git(
        repository, ["symbolic-ref", "--quiet", "--short", "HEAD"], check=False
    )
    branch = (
        branch_result.stdout.decode("utf-8", errors="replace").strip()
        if branch_result.returncode == 0
        else None
    )
    return {
        "full_name": repository.name,
        "description": None,
        "private": None,
        "fork": None,
        "archived": None,
        "default_branch": default_branch(repository),
        "language": None,
        "size": None,
        "topics": [],
        "created_at": None,
        "updated_at": None,
        "pushed_at": None,
        "html_url": remote_origin(repository),
        "current_branch": branch,
        "analyzed_reference": reference,
    }


def cache_parent(repository):
    cache = Path(os.environ.get("REPOLENS_CACHE_DIR", "~/.cache/repolens"))
    return cache.expanduser() / f"local-{repository.name}"


def output_directory(args, repository, mode):
    if args.output:
        return Path(args.output).expanduser()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return cache_parent(repository) / f"{mode}-{args.profile}-{timestamp}"


def validate_args(args):
    for name in (
        "max_files",
        "max_bytes",
        "max_file_bytes",
        "max_patch_bytes",
        "deadline_seconds",
    ):
        if getattr(args, name) <= 0:
            raise RuntimeError(f"--{name.replace('_', '-')} must be greater than zero")
    if args.ref and any(
        (args.base, args.head, args.working_tree, args.patch)
    ):
        raise RuntimeError("--ref cannot be combined with a PR simulation mode")
    if args.head and (args.working_tree or args.patch):
        raise RuntimeError("--head cannot be combined with --working-tree or --patch")
    if args.working_tree and args.patch:
        raise RuntimeError("--working-tree and --patch are mutually exclusive")
    if args.patch and not Path(args.patch).expanduser().is_file():
        raise RuntimeError(f"Patch file not found: {args.patch}")


def collect(args):
    apply_profile(args)
    validate_args(args)
    started_at = time.monotonic()
    progress(args.profile, 1, 4, "Resolving local repository state")
    repository = repository_root(args.repository)
    mode = "repository"
    simulation = None
    warnings = []
    changed_files = []
    patch = None
    pull_metadata = None
    entries = None

    if args.working_tree:
        mode = "pull-request"
        base_ref = args.base or "HEAD"
        base_commit = resolve_commit(repository, base_ref)
        head_commit = resolve_commit(repository, "HEAD")
        patch, changed_files = working_tree_diff(repository, base_commit)
        resolved_ref = head_commit
        analyzed_reference = "working-tree"
        simulation = {
            "kind": "working-tree",
            "base_ref": base_ref,
            "base_commit": base_commit,
            "head_ref": "WORKTREE",
            "head_commit": head_commit,
        }
        warnings.append(
            "Working-tree analysis is mutable; rerun after edits to refresh evidence"
        )
    elif args.patch:
        mode = "pull-request"
        context_ref = args.base or "HEAD"
        base_commit = resolve_commit(repository, context_ref)
        patch_path = Path(args.patch).expanduser().resolve()
        if patch_path.stat().st_size > args.max_patch_bytes:
            raise RuntimeError(
                f"Patch exceeds --max-patch-bytes: {patch_path.stat().st_size}"
            )
        patch = patch_path.read_bytes()
        changed_files = parse_patch(
            patch.decode("utf-8", errors="replace")
        )
        if not changed_files:
            warnings.append(
                "No changed file paths could be parsed from the supplied patch"
            )
        resolved_ref = base_commit
        analyzed_reference = context_ref
        simulation = {
            "kind": "patch-file",
            "base_ref": context_ref,
            "base_commit": base_commit,
            "head_ref": patch_path.name,
            "head_commit": None,
            "patch_path": str(patch_path),
        }
        warnings.append(
            "Patch-file analysis does not apply changes; files/ reflects the context ref"
        )
    elif args.base or args.head:
        mode = "pull-request"
        base_ref = args.base or default_branch(repository)
        head_ref = args.head or "HEAD"
        base_commit = resolve_commit(repository, base_ref)
        head_commit = resolve_commit(repository, head_ref)
        merge_base, patch, changed_files = git_range_diff(
            repository, base_commit, head_commit
        )
        resolved_ref = head_commit
        analyzed_reference = head_ref
        simulation = {
            "kind": "git-range",
            "base_ref": base_ref,
            "base_commit": base_commit,
            "merge_base": merge_base,
            "head_ref": head_ref,
            "head_commit": head_commit,
        }
    else:
        analyzed_reference = args.ref or "HEAD"
        resolved_ref = resolve_commit(repository, analyzed_reference)

    if mode == "pull-request":
        pull_metadata = {
            "number": None,
            "title": f"Local PR simulation: {simulation['kind']}",
            "body": None,
            "state": "local-simulation",
            "draft": None,
            "author": None,
            "base_ref": simulation["base_ref"],
            "base_sha": simulation["base_commit"],
            "head_ref": simulation["head_ref"],
            "head_sha": simulation["head_commit"],
            "head_repository": repository.name,
            "mergeable": None,
            "additions": None,
            "deletions": None,
            "changed_files": len(changed_files),
            "labels": [],
            "html_url": None,
        }

    patch_digest = hashlib.sha256(patch or b"").hexdigest() if patch is not None else None
    fingerprint = collection_fingerprint(
        {
            "provider": "local-git",
            "repository_path": str(repository),
            "mode": mode,
            "resolved_ref": resolved_ref,
            "simulation": simulation,
            "patch_sha256": patch_digest,
            "profile": args.profile,
            "selection_policy_version": SELECTION_POLICY_VERSION,
            "max_files": args.max_files,
            "max_bytes": args.max_bytes,
            "max_file_bytes": args.max_file_bytes,
        }
    )
    progress(args.profile, 2, 4, "Checking exact-state evidence cache")
    if not args.output and not args.no_cache:
        cached = find_cached_snapshot(cache_parent(repository), fingerprint)
        if cached:
            output, manifest = cached
            progress(args.profile, 4, 4, "Cache hit; reusing collected evidence")
            return output, cache_manifest_result(
                manifest, True, time.monotonic() - started_at
            )

    entries = (
        worktree_files(repository)
        if args.working_tree
        else commit_tree(repository, resolved_ref)
    )

    changed_paths = {item["filename"] for item in changed_files}
    candidates = [
        entry
        for entry in entries
        if is_text_candidate(entry["path"], entry.get("size"), args.max_file_bytes)
    ]
    selected, selection = select_candidates(
        candidates, changed_paths, args.max_files, args.max_bytes
    )

    output = output_directory(args, repository, mode)
    if output.exists() and any(output.iterdir()):
        raise RuntimeError(f"Output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    files_root = output / "files"
    files_root.mkdir()
    files_root_resolved = files_root.resolve()

    progress(args.profile, 3, 4, "Sampling architecture layers and collecting files")
    collected_files = []
    failed_files = []
    deadline_reached = False
    for entry in selected:
        if time.monotonic() - started_at >= args.deadline_seconds:
            deadline_reached = True
            break
        try:
            raw = read_entry(repository, entry)
            destination = (files_root / entry["path"]).resolve()
            if not str(destination).startswith(str(files_root_resolved) + os.sep):
                raise RuntimeError("Unsafe repository path")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)
            collected_files.append(
                {
                    "path": entry["path"],
                    "sha": entry.get("sha"),
                    "size": len(raw),
                    "layer": entry["layer"],
                    "changed_in_pull_request": entry["path"] in changed_paths,
                }
            )
        except (OSError, RuntimeError, UnicodeDecodeError) as exc:
            failed_files.append({"path": entry["path"], "reason": str(exc)})

    tree_lines = [
        f"{entry['type']}\t{entry.get('size') or ''}\t{entry['path']}"
        for entry in sorted(entries, key=lambda item: item["path"])
    ]
    (output / "tree.txt").write_text(
        "\n".join(tree_lines) + "\n", encoding="utf-8"
    )
    write_json(output / "recent-commits.json", recent_commits(repository, resolved_ref))

    if mode == "pull-request":
        write_json(output / "pull-request-files.json", changed_files)
        (output / "pull-request.patch").write_bytes(patch or b"")

    selection["layer_planned"] = dict(selection["layer_selected"])
    selection["layer_selected"] = {
        layer: sum(1 for item in collected_files if item.get("layer") == layer)
        for layer in selection["layer_candidates"]
    }
    selection["missing_layers"] = [
        layer
        for layer in selection["layer_candidates"]
        if layer != "other"
        and selection["layer_candidates"].get(layer)
        and not selection["layer_selected"].get(layer)
    ]

    if deadline_reached:
        warnings.append(
            f"Collector stopped at the {args.deadline_seconds}s {args.profile} deadline; "
            "the report must disclose partial evidence coverage"
        )
        selection["deadline_reached"] = True
    else:
        selection["deadline_reached"] = False

    manifest = {
        "schema_version": 2,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "target_url": f"local:{repository}",
        "mode": mode,
        "source": {
            "provider": "local-git",
            "repository_path": str(repository),
            "remote_origin": remote_origin(repository),
        },
        "repository": safe_repository_metadata(repository, analyzed_reference),
        "pull_request": pull_metadata,
        "simulation": simulation,
        "resolved_ref": resolved_ref,
        "profile": args.profile,
        "report_deadline_seconds": PROFILE_DEFAULTS[args.profile][
            "report_deadline_seconds"
        ],
        "collection_fingerprint": fingerprint,
        "tree_source_repository": str(repository),
        "authentication": {"method": "local-filesystem"},
        "limits": {
            "max_files": args.max_files,
            "max_bytes": args.max_bytes,
            "max_file_bytes": args.max_file_bytes,
            "max_patch_bytes": args.max_patch_bytes,
            "deadline_seconds": args.deadline_seconds,
        },
        "selection": selection,
        "stats": {
            "tree_entries": len(entries),
            "text_candidates": len(candidates),
            "collected_files": len(collected_files),
            "collected_bytes": sum(item["size"] for item in collected_files),
            "failed_files": len(failed_files),
            "changed_files": len(changed_files),
        },
        "collected_files": collected_files,
        "failed_files": failed_files,
        "warnings": warnings,
    }
    write_json(output / "manifest.json", manifest)
    progress(args.profile, 4, 4, "Evidence snapshot ready")
    return output.resolve(), cache_manifest_result(
        manifest, False, time.monotonic() - started_at
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Collect a bounded evidence snapshot from a local Git repository."
    )
    parser.add_argument("repository", help="Local Git repository directory")
    parser.add_argument(
        "--profile", choices=sorted(PROFILE_DEFAULTS), default="quick"
    )
    parser.add_argument("--ref", help="Repository-mode Git ref; defaults to HEAD")
    parser.add_argument("--base", help="Base ref for a local PR simulation")
    parser.add_argument("--head", help="Head ref; defaults to HEAD when --base is set")
    parser.add_argument(
        "--working-tree",
        action="store_true",
        help="Compare the working tree, including untracked files, with --base or HEAD",
    )
    parser.add_argument("--patch", help="Downloaded .diff or .patch file")
    parser.add_argument("--output", help="New or empty output directory")
    parser.add_argument("--max-files", type=int)
    parser.add_argument("--max-bytes", type=int)
    parser.add_argument("--max-file-bytes", type=int)
    parser.add_argument("--max-patch-bytes", type=int, default=10_000_000)
    parser.add_argument("--deadline-seconds", type=int)
    parser.add_argument(
        "--no-cache", action="store_true", help="Force a fresh evidence snapshot"
    )
    return parser.parse_args()


def main():
    run_started_at_epoch = time.time()
    args = parse_args()
    output, manifest = collect(args)
    print(
        json.dumps(
            {
                "snapshot": str(output),
                "mode": manifest["mode"],
                "repository": manifest["repository"]["full_name"],
                "authentication": manifest["authentication"]["method"],
                "resolved_ref": manifest["resolved_ref"],
                "simulation": manifest["simulation"],
                "files_collected": manifest["stats"]["collected_files"],
                "profile": manifest.get("profile", args.profile),
                "cache_hit": manifest.get("cache", {}).get("hit", False),
                "elapsed_seconds": manifest.get("cache", {}).get("elapsed_seconds"),
                "run_started_at_epoch": run_started_at_epoch,
                "report_deadline_epoch": run_started_at_epoch
                + PROFILE_DEFAULTS[args.profile]["report_deadline_seconds"],
                "layer_coverage": manifest.get("selection", {}).get(
                    "layer_selected", {}
                ),
                "warnings": manifest["warnings"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        print(f"Local collection failed: {exc}", file=sys.stderr)
        sys.exit(1)
