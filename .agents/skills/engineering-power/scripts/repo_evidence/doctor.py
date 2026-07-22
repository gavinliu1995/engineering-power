#!/usr/bin/env python3
"""Diagnose RepoLens runtime, authentication, and cache configuration."""

import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import sys

from collect_github_context import (
    DEFAULT_CONFIG_PATH,
    GitHubApiError,
    choose_client,
    load_local_config,
    parse_target,
)
from collect_local_context import repository_root
from manage_cache import (
    audit_cache_permissions,
    cache_root,
    retention_policy,
    summarize_cache,
)


def add_check(checks, name, status, detail):
    checks.append({"name": name, "status": status, "detail": detail})


def configured_auth(local_config):
    token_configured = bool(
        os.environ.get("REPOLENS_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    )
    app_id = os.environ.get("REPOLENS_GITHUB_APP_ID") or local_config.get(
        "github_app_id"
    )
    private_key = os.environ.get(
        "REPOLENS_GITHUB_PRIVATE_KEY"
    ) or local_config.get("github_private_key")
    if token_configured:
        source = "environment-token"
    elif os.environ.get("REPOLENS_GITHUB_APP_ID") or os.environ.get(
        "REPOLENS_GITHUB_PRIVATE_KEY"
    ):
        source = "environment-github-app"
    elif app_id or private_key:
        source = "local-config-github-app"
    else:
        source = "anonymous-public-only"
    return source, app_id, private_key


def parse_args():
    parser = argparse.ArgumentParser(
        description="Diagnose RepoLens configuration without exposing credentials."
    )
    parser.add_argument(
        "--repository",
        help="Optional GitHub repository or pull-request URL to test",
    )
    parser.add_argument(
        "--local",
        help="Optional local Git repository directory to test read-only access",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    checks = []

    python_ok = sys.version_info >= (3, 9)
    add_check(
        checks,
        "python",
        "ok" if python_ok else "error",
        f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    )

    config_path = Path(
        os.environ.get("REPOLENS_CONFIG", DEFAULT_CONFIG_PATH)
    ).expanduser()
    try:
        local_config = load_local_config()
        add_check(
            checks,
            "config",
            "ok" if config_path.is_file() else "warning",
            (
                f"Loaded {config_path}"
                if config_path.is_file()
                else f"No local config at {config_path}"
            ),
        )
    except RuntimeError as exc:
        local_config = {}
        add_check(checks, "config", "error", str(exc))

    source, app_id, private_key = configured_auth(local_config)
    if source == "anonymous-public-only":
        add_check(
            checks,
            "authentication",
            "warning",
            "No private-repository credentials configured; public access is available",
        )
    elif source == "environment-token":
        add_check(
            checks,
            "authentication",
            "ok",
            "GitHub token configured through the environment",
        )
    elif not app_id or not private_key:
        add_check(
            checks,
            "authentication",
            "error",
            "GitHub App configuration requires both an App ID and private-key path",
        )
    else:
        key_path = Path(private_key).expanduser()
        if not key_path.is_file():
            add_check(
                checks,
                "authentication",
                "error",
                "GitHub App private-key file does not exist",
            )
        else:
            key_mode = stat.S_IMODE(key_path.stat().st_mode)
            key_status = "warning" if key_mode & 0o077 else "ok"
            add_check(
                checks,
                "authentication",
                key_status,
                f"GitHub App configured through {source}; private-key mode {key_mode:03o}",
            )

    openssl_path = shutil.which("openssl")
    needs_openssl = bool(app_id and private_key and source != "environment-token")
    add_check(
        checks,
        "openssl",
        "ok" if openssl_path else ("error" if needs_openssl else "warning"),
        "OpenSSL available" if openssl_path else "OpenSSL not found in PATH",
    )

    cache = summarize_cache(cache_root())
    add_check(
        checks,
        "cache",
        "ok",
        f"{cache['snapshot_count']} snapshot(s), {cache['total_bytes']} byte(s)",
    )
    cache_permissions = audit_cache_permissions(cache_root())
    insecure_entries = cache_permissions["insecure_entries"]
    add_check(
        checks,
        "cache-permissions",
        "warning" if insecure_entries else "ok",
        (
            f"{insecure_entries} cache path(s) are not private; run "
            "manage_cache.py permissions --fix"
            if insecure_entries
            else "Cache directories are 700 and evidence files are 600"
        ),
    )
    try:
        policy = retention_policy()
        add_check(
            checks,
            "cache-retention",
            "ok",
            (
                f"Keep at most {policy['max_snapshots_per_target']} snapshot(s) "
                f"per target and {policy['max_age_days']} day(s)"
            ),
        )
    except RuntimeError as exc:
        policy = None
        add_check(checks, "cache-retention", "error", str(exc))

    git_path = shutil.which("git")
    add_check(
        checks,
        "git",
        "ok" if git_path else "error",
        "Git available" if git_path else "Git not found in PATH",
    )

    tested_repository = None
    if args.repository:
        try:
            owner, repository, _ = parse_target(args.repository)
            client, authentication = choose_client(
                owner, repository, app_id, private_key
            )
            client.json("GET", f"/repos/{owner}/{repository}")
            tested_repository = f"{owner}/{repository}"
            add_check(
                checks,
                "repository-access",
                "ok",
                f"Read {tested_repository} using {authentication['method']}",
            )
        except (GitHubApiError, RuntimeError, ValueError) as exc:
            add_check(checks, "repository-access", "error", str(exc))

    tested_local_repository = None
    if args.local:
        try:
            tested_local_repository = str(repository_root(args.local))
            add_check(
                checks,
                "local-repository-access",
                "ok",
                f"Read local Git repository {tested_local_repository}",
            )
        except (OSError, RuntimeError, ValueError) as exc:
            add_check(checks, "local-repository-access", "error", str(exc))

    statuses = {check["status"] for check in checks}
    overall = "error" if "error" in statuses else (
        "warning" if "warning" in statuses else "ok"
    )
    result = {
        "status": overall,
        "tested_repository": tested_repository,
        "tested_local_repository": tested_local_repository,
        "checks": checks,
        "cache": {
            key: cache[key]
            for key in (
                "cache_root",
                "snapshot_count",
                "total_bytes",
                "oldest_modified_at",
                "newest_modified_at",
            )
        },
        "cache_retention": policy,
        "cache_permissions": {
            key: cache_permissions[key]
            for key in (
                "directories_checked",
                "files_checked",
                "symlinks_skipped",
                "insecure_entries",
            )
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if overall == "error" else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"RepoLens doctor failed: {exc}", file=sys.stderr)
        sys.exit(1)
