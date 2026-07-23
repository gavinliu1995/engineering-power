#!/usr/bin/env python3
"""Install the portable Engineering Power Agent Skill for a supported host."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


SOURCE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_SOURCE_ROOT = SOURCE_ROOT / ".agents" / "skills"
CORE_SKILL_NAME = "engineering-power"

HOST_PATHS = {
    "copilot": (".agents", "skills"),
    "claude": (".claude", "skills"),
    "cursor": (".cursor", "skills"),
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


def managed_sources() -> tuple[Path, ...]:
    return tuple(
        sorted(
            path
            for path in SKILLS_SOURCE_ROOT.iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        )
    )


def canonical_skill_names() -> set[str]:
    canonical_root = SOURCE_ROOT / "skills"
    return {
        path.name
        for path in canonical_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }


def validate_sources() -> tuple[Path, ...]:
    sources = managed_sources()
    expected_names = canonical_skill_names() | {CORE_SKILL_NAME}
    actual_names = {source.name for source in sources}
    if actual_names != expected_names:
        missing = ", ".join(sorted(expected_names - actual_names)) or "none"
        unexpected = ", ".join(sorted(actual_names - expected_names)) or "none"
        raise RuntimeError(
            "Portable package skill names do not match the canonical suite "
            f"(missing: {missing}; unexpected: {unexpected}). "
            "Run scripts/sync_portable_agent_skill.py."
        )
    core = SKILLS_SOURCE_ROOT / CORE_SKILL_NAME
    required = (
        core / "SKILL.md",
        core / "scripts" / "repo_evidence" / "collect_local_context.py",
        core / "scripts" / "repo_evidence" / "collect_github_context.py",
        core / "scripts" / "repo_evidence" / "finalize_report.py",
        core / "references" / "report-schema.md",
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError("Portable package source is incomplete: " + ", ".join(missing))
    return sources


def remove_destination(destination: Path) -> None:
    if destination.is_symlink() or not destination.is_dir():
        destination.unlink()
    else:
        shutil.rmtree(destination)


def install(
    host: str,
    target_root: Path,
    *,
    force: bool,
    dry_run: bool,
) -> tuple[Path, ...]:
    sources = validate_sources()
    resolved_target_root = target_root.expanduser().resolve()
    resolved_target_root.mkdir(parents=True, exist_ok=True)
    skills_root = destination_for(host, resolved_target_root)
    destinations = tuple(skills_root / source.name for source in sources)

    if dry_run:
        for destination in destinations:
            print(
                f"dry-run: would install Engineering Power Skill for {host} "
                f"at {destination}"
            )
        return destinations

    collisions = tuple(
        destination
        for destination in destinations
        if destination.exists() or destination.is_symlink()
    )
    if collisions and not force:
        collision_list = ", ".join(str(path) for path in collisions)
        raise FileExistsError(
            "Engineering Power Skill destinations already exist: "
            f"{collision_list}. Re-run with --force to replace the managed suite."
        )

    stage_root = Path(
        tempfile.mkdtemp(
            prefix=".engineering-power-stage-",
            dir=resolved_target_root,
        )
    )
    backup_root = None
    installed_destinations: list[Path] = []
    moved_backups: list[tuple[Path, Path]] = []
    try:
        for source in sources:
            shutil.copytree(source, stage_root / source.name)

        skills_root.mkdir(parents=True, exist_ok=True)
        backup_root = Path(
            tempfile.mkdtemp(
                prefix=".engineering-power-backup-",
                dir=resolved_target_root,
            )
        )
        for destination in collisions:
            backup = backup_root / destination.name
            destination.rename(backup)
            moved_backups.append((destination, backup))

        for destination in destinations:
            staged = stage_root / destination.name
            staged.rename(destination)
            installed_destinations.append(destination)
    except Exception:
        for destination in reversed(installed_destinations):
            if destination.exists() or destination.is_symlink():
                remove_destination(destination)
        for destination, backup in reversed(moved_backups):
            if backup.exists() or backup.is_symlink():
                backup.rename(destination)
        raise
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)
        if backup_root is not None:
            shutil.rmtree(backup_root, ignore_errors=True)

    print(
        f"installed {len(destinations)} Engineering Power Skills for {host} "
        f"at {skills_root}"
    )
    return destinations


def main() -> int:
    arguments = parser().parse_args()
    try:
        install(
            arguments.host,
            arguments.target_root,
            force=arguments.force,
            dry_run=arguments.dry_run,
        )
    except (FileExistsError, OSError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
