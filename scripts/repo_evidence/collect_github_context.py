#!/usr/bin/env python3
"""Collect an evidence snapshot for a GitHub repository or pull request.

The collector is deliberately deterministic. It authenticates, resolves the
target commit, downloads a bounded set of text files, and writes metadata for a
Codex skill to analyze. It never prints credentials or stores access tokens.
"""

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib import error, parse, request


API_ROOT = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
API_VERSION = "2022-11-28"
DEFAULT_CONFIG_PATH = "~/.config/repolens/config.json"
SELECTION_POLICY_VERSION = 5

PROFILE_DEFAULTS = {
    "quick": {
        "max_files": 360,
        "max_bytes": 6_000_000,
        "max_file_bytes": 200_000,
        "workers": 10,
        "collector_deadline_seconds": 50,
        "report_deadline_seconds": 120,
    },
    "deep": {
        "max_files": 1200,
        "max_bytes": 16_000_000,
        "max_file_bytes": 300_000,
        "workers": 12,
        "collector_deadline_seconds": 150,
        "report_deadline_seconds": 300,
    },
}

LAYER_ORDER = (
    "core",
    "entrypoint",
    "route",
    "service",
    "persistence",
    "test",
    "operations",
    "other",
)

LAYER_SHARES = {
    "core": 0.08,
    "entrypoint": 0.08,
    "route": 0.18,
    "service": 0.20,
    "persistence": 0.14,
    "test": 0.18,
    "operations": 0.07,
}

TEXT_SUFFIXES = {
    ".bash",
    ".c",
    ".cfg",
    ".cjs",
    ".conf",
    ".cpp",
    ".cs",
    ".css",
    ".csv",
    ".ex",
    ".exs",
    ".gql",
    ".go",
    ".gradle",
    ".graphql",
    ".h",
    ".hcl",
    ".hpp",
    ".htm",
    ".html",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".kts",
    ".less",
    ".md",
    ".mdx",
    ".mjs",
    ".php",
    ".properties",
    ".proto",
    ".py",
    ".rb",
    ".rs",
    ".sass",
    ".scala",
    ".scss",
    ".adoc",
    ".rst",
    ".sh",
    ".sql",
    ".svelte",
    ".swift",
    ".tf",
    ".toml",
    ".ts",
    ".tsx",
    ".tex",
    ".txt",
    ".vue",
    ".xml",
    ".yaml",
    ".yml",
    ".zsh",
}

TEXT_FILENAMES = {
    ".dockerignore",
    ".editorconfig",
    ".env.example",
    ".gitattributes",
    ".gitignore",
    "CODEOWNERS",
    "Dockerfile",
    "Gemfile",
    "Makefile",
    "Procfile",
    "Rakefile",
}

LOCK_FILENAMES = {
    "bun.lock",
    "bun.lockb",
    "Cargo.lock",
    "composer.lock",
    "Gemfile.lock",
    "package-lock.json",
    "Pipfile.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "yarn.lock",
}

EXCLUDED_PARTS = {
    ".git",
    ".gradle",
    ".idea",
    ".next",
    ".nuxt",
    ".pytest_cache",
    ".terraform",
    ".venv",
    ".vscode",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "generated",
    "node_modules",
    "out",
    "target",
    "vendor",
}

SOURCE_PARTS = {
    "api",
    "app",
    "cmd",
    "components",
    "core",
    "domain",
    "handlers",
    "lib",
    "pages",
    "routes",
    "server",
    "services",
    "src",
}

TEST_PARTS = {"__tests__", "e2e", "integration", "spec", "test", "tests"}

MANIFEST_NAMES = {
    "build.gradle",
    "build.gradle.kts",
    "Cargo.toml",
    "composer.json",
    "go.mod",
    "go.sum",
    "mix.exs",
    "package.json",
    "pom.xml",
    "pyproject.toml",
    "requirements.txt",
    "settings.gradle",
    "settings.gradle.kts",
}


class GitHubApiError(RuntimeError):
    def __init__(self, status, message):
        super().__init__(f"GitHub API returned HTTP {status}: {message}")
        self.status = status
        self.message = message


class GitHubClient:
    def __init__(self, token=None):
        self.token = token

    def json(self, method, path, body=None, accept="application/vnd.github+json"):
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {
            "Accept": accept,
            "User-Agent": "repolens-skill",
            "X-GitHub-Api-Version": API_VERSION,
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        api_request = request.Request(
            f"{API_ROOT}{path}", data=data, method=method, headers=headers
        )
        try:
            with request.urlopen(api_request, timeout=30) as response:
                return json.load(response)
        except error.HTTPError as exc:
            message = "unknown GitHub API error"
            try:
                response_body = json.loads(exc.read().decode("utf-8"))
                message = response_body.get("message", message)
            except (ValueError, UnicodeDecodeError):
                pass
            raise GitHubApiError(exc.code, message) from exc
        except error.URLError as exc:
            raise RuntimeError(f"Could not reach GitHub API: {exc.reason}") from exc

    def paginated(self, path, limit_pages=20):
        separator = "&" if "?" in path else "?"
        items = []
        for page in range(1, limit_pages + 1):
            batch = self.json("GET", f"{path}{separator}per_page=100&page={page}")
            if not isinstance(batch, list):
                raise RuntimeError(f"Expected a list from GitHub endpoint: {path}")
            items.extend(batch)
            if len(batch) < 100:
                break
        return items


def base64url(value):
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def create_app_jwt(app_id, private_key_path):
    now = int(time.time())
    header = base64url(b'{"alg":"RS256","typ":"JWT"}')
    payload = base64url(
        json.dumps(
            {"iat": now - 60, "exp": now + (9 * 60), "iss": str(app_id)},
            separators=(",", ":"),
        ).encode("utf-8")
    )
    unsigned_token = f"{header}.{payload}".encode("ascii")
    result = subprocess.run(
        ["openssl", "dgst", "-sha256", "-sign", str(private_key_path)],
        input=unsigned_token,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"OpenSSL could not sign the GitHub App JWT: {detail}")
    return f"{unsigned_token.decode('ascii')}.{base64url(result.stdout)}"


def parse_target(target):
    pattern = re.compile(
        r"^https?://(?:www\.)?github\.com/([^/]+)/([^/?#]+?)(?:\.git)?"
        r"(?:/pull/(\d+))?/?(?:[?#].*)?$"
    )
    match = pattern.match(target.strip())
    if not match:
        raise RuntimeError(
            "Target must be a GitHub repository URL or pull request URL, for example "
            "https://github.com/OWNER/REPO or https://github.com/OWNER/REPO/pull/123"
        )
    owner, repository, pull_number = match.groups()
    return owner, repository, int(pull_number) if pull_number else None


def installation_client(owner, repository, app_id, private_key_path):
    if not app_id or not private_key_path:
        return None, None
    key_path = Path(private_key_path).expanduser()
    if not key_path.is_file():
        return None, None

    app_jwt = create_app_jwt(app_id, key_path)
    app_client = GitHubClient(app_jwt)
    installations = app_client.paginated("/app/installations")
    candidates = [
        item
        for item in installations
        if item.get("account", {}).get("login", "").lower() == owner.lower()
    ]
    for installation in candidates:
        token_response = app_client.json(
            "POST", f"/app/installations/{installation['id']}/access_tokens", {}
        )
        client = GitHubClient(token_response["token"])
        try:
            client.json("GET", f"/repos/{parse.quote(owner)}/{parse.quote(repository)}")
            return client, {
                "method": "github-app",
                "installation_id": installation["id"],
                "account": installation.get("account", {}).get("login"),
                "repository_selection": installation.get("repository_selection"),
            }
        except GitHubApiError as exc:
            if exc.status != 404:
                raise
    return None, None


def repository_access_error(owner, repository, authentication):
    repository_name = f"{owner}/{repository}"
    base = f"Repository {repository_name} was not found or is not accessible."
    if authentication == "environment-token":
        return (
            f"{base} The configured GitHub token cannot read it. Check the token "
            "scope, repository access, and organization SSO authorization."
        )
    if authentication == "github-app":
        return (
            f"{base} GitHub App credentials were detected, but no installation "
            "could read this repository. Install the app for the owner and include "
            "the repository in the installation's repository selection."
        )
    return (
        f"{base} If it is private, configure REPOLENS_GITHUB_TOKEN or install a "
        "GitHub App and configure its App ID and private-key path."
    )


def choose_client(owner, repository, app_id, private_key_path):
    explicit_token = os.environ.get("REPOLENS_GITHUB_TOKEN") or os.environ.get(
        "GITHUB_TOKEN"
    )
    if explicit_token:
        client = GitHubClient(explicit_token)
        try:
            client.json(
                "GET", f"/repos/{parse.quote(owner)}/{parse.quote(repository)}"
            )
        except GitHubApiError as exc:
            if exc.status in {403, 404}:
                raise RuntimeError(
                    repository_access_error(
                        owner, repository, "environment-token"
                    )
                ) from exc
            raise
        return client, {"method": "environment-token"}

    warnings = []
    try:
        client, auth = installation_client(
            owner, repository, app_id, private_key_path
        )
        if client:
            return client, auth
    except (GitHubApiError, RuntimeError) as exc:
        warnings.append(f"GitHub App authentication was unavailable: {exc}")

    client = GitHubClient()
    try:
        repository_data = client.json(
            "GET", f"/repos/{parse.quote(owner)}/{parse.quote(repository)}"
        )
    except GitHubApiError as exc:
        if exc.status == 404:
            authentication = (
                "github-app" if app_id and private_key_path else "anonymous"
            )
            raise RuntimeError(
                repository_access_error(owner, repository, authentication)
            ) from exc
        raise
    if repository_data.get("private"):
        raise RuntimeError("Private repository requires GitHub authentication")
    return client, {"method": "anonymous-public", "warnings": warnings}


def safe_repository_metadata(repository):
    fields = (
        "full_name",
        "description",
        "private",
        "fork",
        "archived",
        "default_branch",
        "language",
        "size",
        "topics",
        "created_at",
        "updated_at",
        "pushed_at",
        "html_url",
    )
    return {field: repository.get(field) for field in fields}


def safe_pull_metadata(pull):
    return {
        "number": pull.get("number"),
        "title": pull.get("title"),
        "body": pull.get("body"),
        "state": pull.get("state"),
        "draft": pull.get("draft"),
        "author": pull.get("user", {}).get("login"),
        "base_ref": pull.get("base", {}).get("ref"),
        "base_sha": pull.get("base", {}).get("sha"),
        "head_ref": pull.get("head", {}).get("ref"),
        "head_sha": pull.get("head", {}).get("sha"),
        "head_repository": pull.get("head", {}).get("repo", {}).get("full_name"),
        "mergeable": pull.get("mergeable"),
        "additions": pull.get("additions"),
        "deletions": pull.get("deletions"),
        "changed_files": pull.get("changed_files"),
        "labels": [label.get("name") for label in pull.get("labels", [])],
        "html_url": pull.get("html_url"),
    }


def safe_commit_metadata(commit):
    details = commit.get("commit", {})
    author = details.get("author") or {}
    return {
        "sha": commit.get("sha"),
        "message": details.get("message"),
        "author_name": author.get("name"),
        "author_date": author.get("date"),
        "author_login": (commit.get("author") or {}).get("login"),
    }


def is_text_candidate(path, size, max_file_bytes):
    file_path = Path(path)
    parts = set(file_path.parts)
    name_lower = file_path.name.lower()
    if parts & EXCLUDED_PARTS:
        return False
    if file_path.name in LOCK_FILENAMES:
        return False
    if file_path.name.endswith((".min.js", ".min.css", ".map")):
        return False
    if size is not None and size > max_file_bytes:
        return False
    documentation_name = any(
        name_lower == prefix or name_lower.startswith(prefix + ".")
        for prefix in ("agents", "changelog", "contributing", "license", "readme")
    )
    return (
        file_path.name in TEXT_FILENAMES
        or file_path.suffix.lower() in TEXT_SUFFIXES
        or documentation_name
    )


def candidate_score(entry, changed_paths):
    path = entry["path"]
    file_path = Path(path)
    parts = set(file_path.parts)
    name_lower = file_path.name.lower()
    score = 0
    if path in changed_paths:
        score += 10000
    if name_lower.startswith("readme") or name_lower.startswith("agents"):
        score += 3500
    if file_path.name in MANIFEST_NAMES:
        score += 3000
    if any(
        token in name_lower
        for token in ("config", "workflow", "pipeline", "docker", "compose")
    ):
        score += 1800
    if parts & SOURCE_PARTS:
        score += 1500
    if parts & TEST_PARTS or "test" in name_lower or "spec" in name_lower:
        score += 1200
    if "docs" in parts or "adr" in parts:
        score += 900
    layer = candidate_layer(path)
    score += {
        "entrypoint": 2600,
        "route": 1500,
        "service": 1500,
        "persistence": 1300,
        "operations": 900,
    }.get(layer, 0)
    if layer == "persistence" and (
        parts & {"dao", "repository", "repositories", "persistence"}
        or any(token in name_lower for token in ("dao", "repository", "datastore"))
    ):
        score += 700
    score -= len(file_path.parts) * 10
    score -= int((entry.get("size") or 0) / 50000)
    return score


def candidate_layer(path):
    """Classify a repository path for deterministic layered sampling."""
    file_path = Path(path)
    parts = {part.lower() for part in file_path.parts}
    name = file_path.name.lower()
    stem = file_path.stem.lower()
    depth = len(file_path.parts)

    if (
        depth == 1
        and (
            name.startswith(("readme", "agents", "contributing", "changelog"))
            or file_path.name in MANIFEST_NAMES
        )
    ) or name in {
        "pom.xml",
        "settings.gradle",
        "settings.gradle.kts",
        "package.json",
        "pyproject.toml",
        "go.mod",
    }:
        return "core"
    if parts & TEST_PARTS or "test" in name or "spec" in name:
        return "test"
    if (
        stem in {"main", "start", "bootstrap", "launcher", "application"}
        or stem.endswith("application")
        or stem.endswith("initializer")
        or name in {"web.xml", "app.yaml", "app.yml"}
    ):
        return "entrypoint"
    if (
        parts & {"routes", "controllers", "controller", "handlers", "pages", "views"}
        or any(token in stem for token in ("route", "controller", "handler", "resource", "endpoint", "page"))
    ):
        return "route"
    if (
        parts & {"services", "service", "usecases", "usecase", "clients", "client"}
        or any(token in stem for token in ("service", "usecase", "facade", "manager", "client", "gateway"))
    ):
        return "service"
    if (
        parts & {"dao", "repository", "repositories", "persistence", "entities", "entity", "models", "model"}
        or any(token in stem for token in ("dao", "repository", "entity", "model", "mapper", "store"))
    ):
        return "persistence"
    if (
        parts & {"deploy", "deployment", "infra", "ops", ".github"}
        or any(token in name for token in ("docker", "compose", "pipeline", "workflow", "helm", "terraform"))
    ):
        return "operations"
    if name.startswith(("readme", "agents")) or file_path.name in MANIFEST_NAMES:
        return "core"
    return "other"


def module_key(path):
    """Return a stable module bucket so a single module cannot fill a layer."""
    parts = Path(path).parts
    if len(parts) <= 1:
        return "_root"
    if parts[0].lower() in {"src", "app", "lib", "test", "tests"}:
        return "_root"
    return parts[0]


def _round_robin(entries):
    buckets = {}
    for entry in entries:
        buckets.setdefault(module_key(entry["path"]), []).append(entry)
    for values in buckets.values():
        values.sort(key=lambda item: (-item["_score"], item["path"]))
    keys = sorted(buckets)
    while keys:
        remaining = []
        for key in keys:
            values = buckets[key]
            if values:
                yield values.pop(0)
            if values:
                remaining.append(key)
        keys = remaining


def select_candidates(candidates, changed_paths, max_files, max_bytes):
    """Select bounded evidence with per-layer and per-module coverage."""
    prepared = []
    for original in candidates:
        entry = dict(original)
        entry["layer"] = candidate_layer(entry["path"])
        entry["_score"] = candidate_score(entry, changed_paths)
        prepared.append(entry)

    by_layer = {layer: [] for layer in LAYER_ORDER}
    for entry in prepared:
        by_layer[entry["layer"]].append(entry)

    selected = []
    selected_paths = set()
    total_bytes = 0

    def add(entry):
        nonlocal total_bytes
        if entry["path"] in selected_paths or len(selected) >= max_files:
            return False
        expected_size = entry.get("size") or 0
        if total_bytes + expected_size > max_bytes:
            return False
        clean = {key: value for key, value in entry.items() if key != "_score"}
        selected.append(clean)
        selected_paths.add(entry["path"])
        total_bytes += expected_size
        return True

    # Changed files are primary PR evidence, but reserve most of the budget for
    # their architectural neighborhood and cross-layer regression context.
    changed_limit = min(max_files // 3, 120)
    changed = sorted(
        (entry for entry in prepared if entry["path"] in changed_paths),
        key=lambda item: (-item["_score"], item["path"]),
    )
    for entry in changed[:changed_limit]:
        add(entry)

    # Root README/build descriptors are anchors for every report and should not
    # compete with module manifests inside the general core quota.
    root_essential_limit = min(12, max(2, max_files // 12))
    root_essentials = sorted(
        (
            entry
            for entry in prepared
            if entry["layer"] == "core" and len(Path(entry["path"]).parts) == 1
        ),
        key=lambda item: (-item["_score"], item["path"]),
    )
    for entry in root_essentials[:root_essential_limit]:
        add(entry)

    for layer in LAYER_ORDER[:-1]:
        quota = max(1, int(max_files * LAYER_SHARES[layer]))
        already = sum(1 for item in selected if item["layer"] == layer)
        for entry in _round_robin(by_layer[layer]):
            if already >= quota or len(selected) >= max_files:
                break
            if add(entry):
                already += 1

    remaining = sorted(
        prepared,
        key=lambda item: (-item["_score"], item["layer"], item["path"]),
    )
    for entry in _round_robin(remaining):
        if len(selected) >= max_files:
            break
        add(entry)

    layer_candidates = {
        layer: len(values) for layer, values in by_layer.items()
    }
    layer_selected = {
        layer: sum(1 for item in selected if item["layer"] == layer)
        for layer in LAYER_ORDER
    }
    missing_layers = [
        layer
        for layer in LAYER_ORDER[:-1]
        if layer_candidates[layer] and not layer_selected[layer]
    ]
    unavailable_layers = [
        layer for layer in LAYER_ORDER[:-1] if not layer_candidates[layer]
    ]
    changed_candidate_paths = {entry["path"] for entry in changed}
    return selected, {
        "policy_version": SELECTION_POLICY_VERSION,
        "layer_candidates": layer_candidates,
        "layer_selected": layer_selected,
        "missing_layers": missing_layers,
        "unavailable_layers": unavailable_layers,
        "changed_files_requested": len(changed_paths),
        "changed_text_candidates": len(changed),
        "changed_selected": sum(
            1 for item in selected if item["path"] in changed_paths
        ),
        "changed_files_not_text_candidates": sorted(
            changed_paths - changed_candidate_paths
        ),
        "changed_files_not_selected": sorted(
            changed_candidate_paths - selected_paths
        ),
        "truncated_by_file_limit": len(selected) < len(prepared) and len(selected) >= max_files,
        "truncated_by_byte_limit": total_bytes >= max_bytes or any(
            (entry.get("size") or 0) + total_bytes > max_bytes
            for entry in prepared
            if entry["path"] not in selected_paths
        ),
    }


def apply_profile(args):
    defaults = PROFILE_DEFAULTS[args.profile]
    for name in (
        "max_files",
        "max_bytes",
        "max_file_bytes",
        "workers",
        "deadline_seconds",
    ):
        if getattr(args, name, None) is None:
            source = (
                "collector_deadline_seconds"
                if name == "deadline_seconds"
                else name
            )
            setattr(args, name, defaults[source])
    return args


def progress(profile, step, total, message):
    print(
        f"[RepoLens {profile.title()} {step}/{total}] {message}",
        file=sys.stderr,
        flush=True,
    )


def collection_fingerprint(payload):
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def find_cached_snapshot(parent, fingerprint):
    if not parent.is_dir():
        return None
    manifests = sorted(
        parent.glob("*/manifest.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for manifest_path in manifests:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if (
            manifest.get("collection_fingerprint") == fingerprint
            and manifest.get("selection", {}).get("policy_version")
            == SELECTION_POLICY_VERSION
            and (manifest_path.parent / "files").is_dir()
        ):
            return manifest_path.parent.resolve(), manifest
    return None


def cache_manifest_result(manifest, hit, elapsed_seconds):
    result = dict(manifest)
    result["cache"] = {
        "hit": hit,
        "elapsed_seconds": round(elapsed_seconds, 3),
    }
    return result


def decode_blob(blob):
    if blob.get("encoding") != "base64":
        raise RuntimeError("GitHub returned a blob using an unsupported encoding")
    raw = base64.b64decode(blob.get("content", ""), validate=False)
    if b"\x00" in raw:
        raise RuntimeError("Blob appears to be binary")
    raw.decode("utf-8")
    return raw


def write_json(path, value):
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def load_local_config():
    config_path = Path(
        os.environ.get("REPOLENS_CONFIG", DEFAULT_CONFIG_PATH)
    ).expanduser()
    if not config_path.exists():
        return {}
    if not config_path.is_file():
        raise RuntimeError(f"RepoLens config is not a file: {config_path}")
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RuntimeError(
            f"Could not read RepoLens config {config_path}: {exc}"
        ) from exc
    if not isinstance(config, dict):
        raise RuntimeError(f"RepoLens config must contain a JSON object: {config_path}")
    return config


def resolve_github_app_settings(app_id=None, private_key=None):
    app_id = app_id or os.environ.get("REPOLENS_GITHUB_APP_ID")
    private_key = private_key or os.environ.get("REPOLENS_GITHUB_PRIVATE_KEY")
    explicit_token = os.environ.get("REPOLENS_GITHUB_TOKEN") or os.environ.get(
        "GITHUB_TOKEN"
    )
    if explicit_token or (app_id and private_key):
        return app_id, private_key

    local_config = load_local_config()
    return (
        app_id or local_config.get("github_app_id"),
        private_key or local_config.get("github_private_key"),
    )


def collect(args):
    apply_profile(args)
    for name in ("max_files", "max_bytes", "max_file_bytes", "workers", "deadline_seconds"):
        if getattr(args, name) <= 0:
            raise RuntimeError(f"--{name.replace('_', '-')} must be greater than zero")
    started_at = time.monotonic()
    progress(args.profile, 1, 4, "Resolving target and exact commit")
    owner, repository_name, pull_number = parse_target(args.target)
    client, authentication = choose_client(
        owner, repository_name, args.app_id, args.private_key
    )
    repository_path = f"/repos/{parse.quote(owner)}/{parse.quote(repository_name)}"
    repository = client.json("GET", repository_path)

    mode = "pull-request" if pull_number else "repository"
    warnings = list(authentication.pop("warnings", []))
    pull_metadata = None
    changed_files = []
    changed_paths = set()
    tree_owner = owner
    tree_repository = repository_name

    if pull_number:
        pull = client.json("GET", f"{repository_path}/pulls/{pull_number}")
        pull_metadata = safe_pull_metadata(pull)
        changed_files = client.paginated(f"{repository_path}/pulls/{pull_number}/files")
        changed_paths = {item.get("filename") for item in changed_files}
        ref = pull_metadata["head_sha"]
        head_repository = pull_metadata.get("head_repository")
        if head_repository and "/" in head_repository:
            tree_owner, tree_repository = head_repository.split("/", 1)
    else:
        ref = repository.get("default_branch")

    tree_repository_path = (
        f"/repos/{parse.quote(tree_owner)}/{parse.quote(tree_repository)}"
    )
    if not pull_number:
        commit = client.json("GET", f"{repository_path}/commits/{parse.quote(ref)}")
        ref = commit.get("sha")

    fingerprint = collection_fingerprint(
        {
            "provider": "github",
            "target": f"{owner}/{repository_name}",
            "mode": mode,
            "pull_number": pull_number,
            "resolved_ref": ref,
            "base_ref": (pull_metadata or {}).get("base_sha"),
            "change_fingerprint": collection_fingerprint(
                [
                    {
                        "filename": item.get("filename"),
                        "status": item.get("status"),
                        "sha": item.get("sha"),
                        "patch": item.get("patch"),
                    }
                    for item in changed_files
                ]
            )
            if changed_files
            else None,
            "profile": args.profile,
            "selection_policy_version": SELECTION_POLICY_VERSION,
            "max_files": args.max_files,
            "max_bytes": args.max_bytes,
            "max_file_bytes": args.max_file_bytes,
        }
    )
    cache_parent = (
        Path(os.environ.get("REPOLENS_CACHE_DIR", "~/.cache/repolens"))
        .expanduser()
        / f"{owner}-{repository_name}"
    )
    progress(args.profile, 2, 4, "Checking exact-commit evidence cache")
    if not args.output and not args.no_cache:
        cached = find_cached_snapshot(cache_parent, fingerprint)
        if cached:
            output, manifest = cached
            progress(args.profile, 4, 4, "Cache hit; reusing collected evidence")
            return output, cache_manifest_result(
                manifest, True, time.monotonic() - started_at
            )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = (
        Path(args.output).expanduser()
        if args.output
        else cache_parent
        / f"{mode}-{pull_number or 'default'}-{args.profile}-{timestamp}"
    )
    if output.exists() and any(output.iterdir()):
        raise RuntimeError(f"Output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    files_root = output / "files"
    files_root.mkdir()

    progress(args.profile, 3, 4, "Sampling architecture layers and collecting files")
    tree_response = client.json(
        "GET", f"{tree_repository_path}/git/trees/{parse.quote(ref)}?recursive=1"
    )
    tree = tree_response.get("tree", [])
    if tree_response.get("truncated"):
        warnings.append("GitHub returned a truncated recursive tree")

    if pull_number:
        recent_commits_raw = client.paginated(
            f"{repository_path}/pulls/{pull_number}/commits", limit_pages=5
        )
    else:
        recent_commits_raw = client.json("GET", f"{repository_path}/commits?per_page=20")
    recent_commits = [safe_commit_metadata(item) for item in recent_commits_raw]

    candidates = [
        entry
        for entry in tree
        if entry.get("type") == "blob"
        and is_text_candidate(entry["path"], entry.get("size"), args.max_file_bytes)
    ]
    selected, selection = select_candidates(
        candidates, changed_paths, args.max_files, args.max_bytes
    )

    def fetch_entry(entry):
        path = entry["path"]
        try:
            blob = client.json(
                "GET", f"{tree_repository_path}/git/blobs/{entry['sha']}"
            )
            raw = decode_blob(blob)
            return (
                entry,
                raw,
                {
                    "path": path,
                    "sha": entry.get("sha"),
                    "size": len(raw),
                    "layer": entry["layer"],
                    "changed_in_pull_request": path in changed_paths,
                },
                None,
            )
        except (GitHubApiError, RuntimeError, UnicodeDecodeError) as exc:
            return entry, None, None, {"path": path, "reason": str(exc)}

    collected_files = []
    failed_files = []
    files_root_resolved = files_root.resolve()
    worker_count = max(1, min(args.workers, len(selected) or 1))
    deadline_reached = False
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        for offset in range(0, len(selected), worker_count):
            if time.monotonic() - started_at >= args.deadline_seconds:
                deadline_reached = True
                break
            batch = selected[offset : offset + worker_count]
            futures = [executor.submit(fetch_entry, entry) for entry in batch]
            for future in as_completed(futures):
                entry, raw, collected, failed = future.result()
                if failed:
                    failed_files.append(failed)
                    continue
                destination = (files_root / entry["path"]).resolve()
                if not str(destination).startswith(str(files_root_resolved) + os.sep):
                    failed_files.append(
                        {"path": entry["path"], "reason": "Unsafe repository path"}
                    )
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(raw)
                collected_files.append(collected)

    collected_files.sort(key=lambda item: item["path"])
    failed_files.sort(key=lambda item: item["path"])
    selection["layer_planned"] = dict(selection["layer_selected"])
    selection["layer_selected"] = {
        layer: sum(1 for item in collected_files if item.get("layer") == layer)
        for layer in LAYER_ORDER
    }
    selection["missing_layers"] = [
        layer
        for layer in LAYER_ORDER[:-1]
        if selection["layer_candidates"].get(layer)
        and not selection["layer_selected"].get(layer)
    ]
    selection["unavailable_layers"] = [
        layer
        for layer in LAYER_ORDER[:-1]
        if not selection["layer_candidates"].get(layer)
    ]
    collected_paths = {item["path"] for item in collected_files}
    selection["changed_collected"] = sum(
        1 for path in collected_paths if path in changed_paths
    )
    selection["changed_files_missing_from_snapshot"] = sorted(
        changed_paths - collected_paths
    )

    tree_lines = []
    for entry in sorted(tree, key=lambda item: item.get("path", "")):
        size = "" if entry.get("size") is None else str(entry.get("size"))
        tree_lines.append(f"{entry.get('type', '')}\t{size}\t{entry.get('path', '')}")
    (output / "tree.txt").write_text("\n".join(tree_lines) + "\n", encoding="utf-8")

    if changed_files:
        safe_changed_files = []
        patch_sections = []
        for item in changed_files:
            safe_item = {
                key: item.get(key)
                for key in (
                    "filename",
                    "status",
                    "additions",
                    "deletions",
                    "changes",
                    "previous_filename",
                    "patch",
                )
            }
            safe_changed_files.append(safe_item)
            patch_sections.append(
                f"diff --git a/{item.get('filename')} b/{item.get('filename')}\n"
                f"{item.get('patch') or '[Patch unavailable or binary file]'}"
            )
        write_json(output / "pull-request-files.json", safe_changed_files)
        (output / "pull-request.patch").write_text(
            "\n\n".join(patch_sections) + "\n", encoding="utf-8"
        )

    write_json(output / "recent-commits.json", recent_commits)
    selection["deadline_reached"] = deadline_reached
    if deadline_reached:
        warnings.append(
            f"Collector stopped at the {args.deadline_seconds}s {args.profile} deadline; "
            "the report must disclose partial evidence coverage"
        )

    manifest = {
        "schema_version": 2,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "target_url": args.target,
        "mode": mode,
        "repository": safe_repository_metadata(repository),
        "pull_request": pull_metadata,
        "resolved_ref": ref,
        "profile": args.profile,
        "report_deadline_seconds": PROFILE_DEFAULTS[args.profile][
            "report_deadline_seconds"
        ],
        "collection_fingerprint": fingerprint,
        "tree_source_repository": f"{tree_owner}/{tree_repository}",
        "authentication": authentication,
        "limits": {
            "max_files": args.max_files,
            "max_bytes": args.max_bytes,
            "max_file_bytes": args.max_file_bytes,
            "workers": worker_count,
            "deadline_seconds": args.deadline_seconds,
        },
        "selection": selection,
        "stats": {
            "tree_entries": len(tree),
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
        description="Collect a bounded local evidence snapshot from a GitHub repo or PR."
    )
    parser.add_argument("target", help="GitHub repository or pull request URL")
    parser.add_argument(
        "--profile", choices=sorted(PROFILE_DEFAULTS), default="quick"
    )
    parser.add_argument("--output", help="New or empty output directory")
    parser.add_argument(
        "--app-id",
        default=None,
        help="GitHub App ID; override with REPOLENS_GITHUB_APP_ID",
    )
    parser.add_argument(
        "--private-key",
        default=None,
        help="GitHub App private key path; override with REPOLENS_GITHUB_PRIVATE_KEY",
    )
    parser.add_argument("--max-files", type=int)
    parser.add_argument("--max-bytes", type=int)
    parser.add_argument("--max-file-bytes", type=int)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--deadline-seconds", type=int)
    parser.add_argument(
        "--no-cache", action="store_true", help="Force a fresh evidence snapshot"
    )
    args = parser.parse_args()
    args.app_id, args.private_key = resolve_github_app_settings(
        args.app_id, args.private_key
    )
    return args


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
    except (RuntimeError, GitHubApiError, KeyError, ValueError) as exc:
        print(f"Collection failed: {exc}", file=sys.stderr)
        sys.exit(1)
