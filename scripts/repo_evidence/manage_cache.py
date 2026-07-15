#!/usr/bin/env python3
"""Inspect and safely clean RepoLens evidence snapshots."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sys
import time

from cache_permissions import audit_tree, secure_tree


DEFAULT_CACHE_PATH = "~/.cache/repolens"
DEFAULT_CONFIG_PATH = "~/.config/repolens/config.json"
DEFAULT_RETENTION_POLICY = {
    "max_age_days": 30,
    "max_snapshots_per_target": 5,
}


def cache_root():
    return Path(
        os.environ.get("REPOLENS_CACHE_DIR", DEFAULT_CACHE_PATH)
    ).expanduser()


def retention_policy(config_path=None, overrides=None):
    path = Path(
        config_path
        or os.environ.get("REPOLENS_CONFIG", DEFAULT_CONFIG_PATH)
    ).expanduser()
    configured = {}
    if path.is_file():
        try:
            content = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise RuntimeError(
                f"Could not read RepoLens config {path}: {exc}"
            ) from exc
        if not isinstance(content, dict):
            raise RuntimeError(f"RepoLens config must contain a JSON object: {path}")
        configured = content.get("cache_retention", {})
        if not isinstance(configured, dict):
            raise RuntimeError("cache_retention must contain a JSON object")

    policy = {**DEFAULT_RETENTION_POLICY, **configured, **(overrides or {})}
    max_age = policy.get("max_age_days")
    max_per_target = policy.get("max_snapshots_per_target")
    if not isinstance(max_age, int) or isinstance(max_age, bool) or max_age < 0:
        raise RuntimeError("cache_retention.max_age_days must be a non-negative integer")
    if (
        not isinstance(max_per_target, int)
        or isinstance(max_per_target, bool)
        or max_per_target < 1
    ):
        raise RuntimeError(
            "cache_retention.max_snapshots_per_target must be a positive integer"
        )
    return {
        "max_age_days": max_age,
        "max_snapshots_per_target": max_per_target,
        "config_path": str(path),
        "config_exists": path.is_file(),
    }


def directory_size(path):
    total = 0
    for current, directories, files in os.walk(path, followlinks=False):
        current_path = Path(current)
        directories[:] = [
            name for name in directories if not (current_path / name).is_symlink()
        ]
        for name in files:
            file_path = current_path / name
            if file_path.is_symlink():
                continue
            try:
                total += file_path.stat().st_size
            except OSError:
                continue
    return total


def find_snapshots(root):
    root = root.expanduser().resolve()
    if not root.is_dir():
        return []

    snapshots = []
    for current, directories, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        directories[:] = [
            name for name in directories if not (current_path / name).is_symlink()
        ]
        if "manifest.json" not in files:
            continue
        resolved = current_path.resolve()
        if not str(resolved).startswith(str(root) + os.sep):
            continue
        manifest_path = resolved / "manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            modified_at = manifest_path.stat().st_mtime
        except (OSError, ValueError):
            manifest = {}
            modified_at = resolved.stat().st_mtime
        snapshots.append(
            {
                "path": str(resolved),
                "relative_path": str(resolved.relative_to(root)),
                "bytes": directory_size(resolved),
                "modified_at": modified_at,
                "collected_at": manifest.get("collected_at"),
                "target_url": manifest.get("target_url"),
                "mode": manifest.get("mode"),
            }
        )
        directories[:] = []
    return sorted(snapshots, key=lambda item: item["modified_at"])


def format_timestamp(timestamp):
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat()


def summarize_cache(root):
    root = root.expanduser().resolve()
    snapshots = find_snapshots(root)
    return {
        "cache_root": str(root),
        "exists": root.is_dir(),
        "snapshot_count": len(snapshots),
        "total_bytes": sum(item["bytes"] for item in snapshots),
        "oldest_modified_at": format_timestamp(
            snapshots[0]["modified_at"] if snapshots else None
        ),
        "newest_modified_at": format_timestamp(
            snapshots[-1]["modified_at"] if snapshots else None
        ),
        "snapshots": [
            {
                **item,
                "modified_at": format_timestamp(item["modified_at"]),
            }
            for item in snapshots
        ],
    }


def audit_cache_permissions(root):
    return audit_tree(Path(root).expanduser())


def secure_cache_permissions(root):
    root = Path(root).expanduser()
    before = audit_tree(root)
    secured = secure_tree(root)
    after = audit_tree(root)
    return {
        "cache_root": str(root.resolve()),
        "fixed_entries": before["insecure_entries"],
        "insecure_entries": after["insecure_entries"],
        "remaining_insecure_entries": after["insecure_entries"],
        "symlinks_skipped": secured["symlinks_skipped"],
        "directories_secured": secured["directories"],
        "files_secured": secured["files"],
    }


def select_snapshots(snapshots, older_than_days=None, delete_all=False, now=None):
    if delete_all:
        return list(snapshots)
    now = time.time() if now is None else now
    cutoff = now - (older_than_days * 86400)
    return [item for item in snapshots if item["modified_at"] < cutoff]


def select_by_retention_policy(snapshots, policy, now=None):
    now = time.time() if now is None else now
    cutoff = now - (policy["max_age_days"] * 86400)
    selected = {}

    for snapshot in snapshots:
        if snapshot["modified_at"] < cutoff:
            selected.setdefault(snapshot["path"], set()).add("max-age")

    grouped = {}
    for snapshot in snapshots:
        target = snapshot.get("target_url") or snapshot["relative_path"].split(
            os.sep, 1
        )[0]
        grouped.setdefault(target, []).append(snapshot)
    for target_snapshots in grouped.values():
        newest_first = sorted(
            target_snapshots, key=lambda item: item["modified_at"], reverse=True
        )
        for snapshot in newest_first[policy["max_snapshots_per_target"] :]:
            selected.setdefault(snapshot["path"], set()).add("max-per-target")

    result = []
    for snapshot in snapshots:
        reasons = selected.get(snapshot["path"])
        if reasons:
            result.append(
                {**snapshot, "retention_reasons": sorted(reasons)}
            )
    return result


def delete_snapshots(root, snapshots, confirm=False):
    root = root.expanduser().resolve()
    deleted = []
    reclaimed_bytes = 0
    if not confirm:
        return deleted, reclaimed_bytes

    for snapshot in snapshots:
        snapshot_path = Path(snapshot["path"]).resolve()
        if not str(snapshot_path).startswith(str(root) + os.sep):
            raise RuntimeError(f"Refusing to delete outside cache root: {snapshot_path}")
        if snapshot_path.is_symlink() or not (snapshot_path / "manifest.json").is_file():
            raise RuntimeError(f"Refusing to delete unsafe snapshot: {snapshot_path}")
        shutil.rmtree(snapshot_path)
        deleted.append(snapshot["relative_path"])
        reclaimed_bytes += snapshot["bytes"]

        parent = snapshot_path.parent
        while parent != root:
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent
    return deleted, reclaimed_bytes


def parse_args():
    parser = argparse.ArgumentParser(
        description="Inspect or safely clean RepoLens evidence snapshots."
    )
    parser.add_argument(
        "--cache-dir",
        default=str(cache_root()),
        help="Cache root; defaults to REPOLENS_CACHE_DIR or ~/.cache/repolens",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", help="Show cache usage and snapshots")
    permissions_parser = subparsers.add_parser(
        "permissions", help="Audit private cache permissions or repair them"
    )
    permissions_parser.add_argument(
        "--fix",
        action="store_true",
        help="Set cache directories to 700 and evidence files to 600",
    )

    clean_parser = subparsers.add_parser(
        "clean", help="Preview or delete matching snapshots"
    )
    selector = clean_parser.add_mutually_exclusive_group(required=True)
    selector.add_argument(
        "--older-than-days",
        type=int,
        help="Select snapshots older than this many days",
    )
    selector.add_argument("--all", action="store_true", help="Select all snapshots")
    clean_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Actually delete; without this option the command is a dry run",
    )

    prune_parser = subparsers.add_parser(
        "prune", help="Preview or enforce the configured retention policy"
    )
    prune_parser.add_argument(
        "--config",
        help="RepoLens config path; defaults to REPOLENS_CONFIG or ~/.config/repolens/config.json",
    )
    prune_parser.add_argument(
        "--max-age-days",
        type=int,
        help="Override cache_retention.max_age_days",
    )
    prune_parser.add_argument(
        "--max-snapshots-per-target",
        type=int,
        help="Override cache_retention.max_snapshots_per_target",
    )
    prune_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Actually delete; without this option the command is a dry run",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root = Path(args.cache_dir).expanduser().resolve()
    summary = summarize_cache(root)
    if args.command == "status":
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    if args.command == "permissions":
        result = (
            secure_cache_permissions(root)
            if args.fix
            else audit_cache_permissions(root)
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if not result.get("insecure_entries") else 1

    if args.command == "prune":
        overrides = {
            key: value
            for key, value in {
                "max_age_days": args.max_age_days,
                "max_snapshots_per_target": args.max_snapshots_per_target,
            }.items()
            if value is not None
        }
        policy = retention_policy(args.config, overrides)
        selected = select_by_retention_policy(find_snapshots(root), policy)
        deleted, reclaimed_bytes = delete_snapshots(
            root, selected, confirm=args.confirm
        )
        result = {
            "cache_root": str(root),
            "dry_run": not args.confirm,
            "policy": policy,
            "matched_snapshots": len(selected),
            "matched_bytes": sum(item["bytes"] for item in selected),
            "matches": [
                {
                    "relative_path": item["relative_path"],
                    "target_url": item.get("target_url"),
                    "reasons": item["retention_reasons"],
                }
                for item in selected
            ],
            "deleted_snapshots": deleted,
            "reclaimed_bytes": reclaimed_bytes,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.older_than_days is not None and args.older_than_days < 0:
        raise RuntimeError("--older-than-days must be zero or greater")
    snapshots = find_snapshots(root)
    selected = select_snapshots(
        snapshots,
        older_than_days=args.older_than_days,
        delete_all=args.all,
    )
    deleted, reclaimed_bytes = delete_snapshots(
        root, selected, confirm=args.confirm
    )
    result = {
        "cache_root": str(root),
        "dry_run": not args.confirm,
        "matched_snapshots": len(selected),
        "matched_bytes": sum(item["bytes"] for item in selected),
        "deleted_snapshots": deleted,
        "reclaimed_bytes": reclaimed_bytes,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Cache operation failed: {exc}", file=sys.stderr)
        sys.exit(1)
