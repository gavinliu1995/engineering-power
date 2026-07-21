#!/usr/bin/env python3
"""Install the portable Engineering Power Agent Skill for a supported host."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys


SOURCE_ROOT = Path(__file__).resolve().parents[1]
SKILL_SOURCE = SOURCE_ROOT / ".agents" / "skills" / "engineering-power"
EVIDENCE_SOURCE = SOURCE_ROOT / "scripts" / "repo_evidence"
REFERENCE_SOURCE = SOURCE_ROOT / "references"

HOST_PATHS = {
    "copilot": (".agents", "skills", "engineering-power"),
    "claude": (".claude", "skills", "engineering-power"),
    "cursor": (".cursor", "skills", "engineering-power"),
}


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        description="Install the portable Engineering Power Agent Skill."
    )
    command.add_argument("--host", choices=sorted(HOST_PATHS), required=True)
    command.add_argument(
        "--target-root",
        type=Path,
        required=True,
        help="Repository root for a project installation, or home directory for a user installation.",
    )
    command.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing Engineering Power destination.",
    )
    command.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the target without creating or replacing files.",
    )
    return command


def destination_for(host: str, target_root: Path) -> Path:
    return target_root.joinpath(*HOST_PATHS[host])


def validate_sources() -> None:
    required = (
        SKILL_SOURCE / "SKILL.md",
        EVIDENCE_SOURCE / "collect_local_context.py",
        EVIDENCE_SOURCE / "collect_github_context.py",
        EVIDENCE_SOURCE / "finalize_report.py",
        REFERENCE_SOURCE / "report-schema.md",
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError("Portable package source is incomplete: " + ", ".join(missing))


def install(host: str, target_root: Path, *, force: bool, dry_run: bool) -> Path:
    validate_sources()
    destination = destination_for(host, target_root.expanduser().resolve())
    if dry_run:
        print(f"dry-run: would install Engineering Power for {host} at {destination}")
        return destination

    if destination.exists():
        if not force:
            raise FileExistsError(
                f"Destination already exists: {destination}. Re-run with --force to replace it."
            )
        if destination.is_symlink():
            destination.unlink()
        elif destination.is_dir():
            shutil.rmtree(destination)
        else:
            destination.unlink()

    destination.mkdir(parents=True, exist_ok=False)
    shutil.copy2(SKILL_SOURCE / "SKILL.md", destination / "SKILL.md")
    shutil.copytree(EVIDENCE_SOURCE, destination / "scripts" / "repo_evidence")
    shutil.copytree(REFERENCE_SOURCE, destination / "references")
    print(f"installed Engineering Power for {host} at {destination}")
    return destination


def main() -> int:
    arguments = parser().parse_args()
    try:
        install(
            arguments.host,
            arguments.target_root,
            force=arguments.force,
            dry_run=arguments.dry_run,
        )
    except (FileExistsError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
