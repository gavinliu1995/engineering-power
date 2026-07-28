#!/usr/bin/env python3
"""Install the portable Engineering Power Agent Skill for a supported host.

Generates portable skill packages on-the-fly from the canonical skills/
directory, bundling the evidence engine and references into the core skill.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


SOURCE_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = SOURCE_ROOT / "skills"
CORE_SKILL_NAME = "engineering-power"
REPO_EVIDENCE_DIR = SOURCE_ROOT / "scripts" / "repo_evidence"
REFERENCES_DIR = SOURCE_ROOT / "references"

HOST_PATHS = {
    "copilot": (".agents", "skills"),
    "claude": (".claude", "skills"),
    "cursor": (".cursor", "skills"),
}

EXCLUDED_PARTS = {"agents", "__pycache__"}

PORTABLE_RUNTIME = """\

## Portable runtime

This skill is part of the Engineering Power suite. Resolve the evidence engine
from `../engineering-power/scripts/repo_evidence/` and shared report schemas
from `../engineering-power/references/`. Do not bypass the evidence engine for
repository, pull-request, comparison, working-tree, or patch analysis.
"""


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


def discover_skills() -> list[Path]:
    """Find all canonical skill directories under skills/<name>/."""
    skills = []
    for skill_dir in sorted(SKILLS_ROOT.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue
        if (skill_dir / "SKILL.md").is_file():
            skills.append(skill_dir)
    return skills


def canonical_skill_names() -> set[str]:
    return {skill.name for skill in discover_skills()}


def included_file(path: Path, source: Path) -> bool:
    """Return True if a file should be included in the portable package."""
    relative = path.relative_to(source)
    return (
        path.is_file()
        and not EXCLUDED_PARTS.intersection(relative.parts)
        and path.suffix != ".pyc"
    )


def transform_skill_md(content: str, skill_name: str) -> str:
    """Transform a canonical SKILL.md for portable distribution."""
    # Remove old Codex-specific path references
    transformed = content.replace("$PLUGIN_ROOT", "$ENGINEERING_POWER_CORE")
    transformed = transformed.replace("engineering-power:", "")

    # For non-core skills, inject portable runtime section after frontmatter
    if skill_name != CORE_SKILL_NAME:
        frontmatter_end = transformed.find("\n---", 4)
        if frontmatter_end >= 0:
            insertion_point = frontmatter_end + len("\n---")
            transformed = (
                transformed[:insertion_point]
                + PORTABLE_RUNTIME
                + transformed[insertion_point:]
            )

    return transformed


def generate_portable_skill(source: Path, destination: Path) -> None:
    """Generate a portable skill package from a canonical source."""
    destination.mkdir(parents=True, exist_ok=True)
    for source_path in source.rglob("*"):
        if not included_file(source_path, source):
            continue
        relative = source_path.relative_to(source)
        dest_path = destination / relative
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        if relative == Path("SKILL.md"):
            dest_path.write_text(
                transform_skill_md(
                    source_path.read_text(encoding="utf-8"),
                    source.name,
                ),
                encoding="utf-8",
            )
        else:
            shutil.copy2(source_path, dest_path)


def generate_core_skill(destination: Path) -> None:
    """Generate the engineering-power core skill with bundled runtime."""
    # Find the core skill source
    core_source = None
    for skill in discover_skills():
        if skill.name == CORE_SKILL_NAME:
            core_source = skill
            break

    if core_source is None:
        raise RuntimeError(
            f"Core skill '{CORE_SKILL_NAME}' not found in skills/"
        )

    # Generate the skill itself
    generate_portable_skill(core_source, destination)

    # Bundle repo_evidence scripts
    evidence_dest = destination / "scripts" / "repo_evidence"
    if REPO_EVIDENCE_DIR.is_dir():
        shutil.copytree(
            REPO_EVIDENCE_DIR,
            evidence_dest,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )

    # Bundle references
    references_dest = destination / "references"
    if REFERENCES_DIR.is_dir():
        shutil.copytree(
            REFERENCES_DIR,
            references_dest,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )


def validate_sources() -> list[Path]:
    """Validate that the canonical skills are present and complete."""
    skills = discover_skills()
    if not skills:
        raise RuntimeError("No skills found in skills/")

    # Verify core skill exists
    names = {skill.name for skill in skills}
    if CORE_SKILL_NAME not in names:
        raise RuntimeError(
            f"Core skill '{CORE_SKILL_NAME}' not found. "
            f"Expected at skills/{CORE_SKILL_NAME}/SKILL.md"
        )

    # Verify evidence engine
    required = (
        REPO_EVIDENCE_DIR / "collect_local_context.py",
        REPO_EVIDENCE_DIR / "collect_github_context.py",
        REPO_EVIDENCE_DIR / "finalize_report.py",
        REFERENCES_DIR / "report-schema.md",
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(
            "Evidence engine is incomplete: " + ", ".join(missing)
        )

    return skills


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
    skills = validate_sources()
    resolved_target_root = target_root.expanduser().resolve()
    skills_root = destination_for(host, resolved_target_root)
    skill_names = [skill.name for skill in skills]
    destinations = tuple(skills_root / name for name in skill_names)

    if dry_run:
        for destination in destinations:
            print(
                f"dry-run: would install Engineering Power Skill for {host} "
                f"at {destination}"
            )
        return destinations

    resolved_target_root.mkdir(parents=True, exist_ok=True)
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

    # Generate portable package in a staging directory
    stage_root = Path(
        tempfile.mkdtemp(
            prefix=".engineering-power-stage-",
            dir=resolved_target_root,
        )
    )
    backup_root = None
    preserve_backup = False
    installed_destinations: list[Path] = []
    moved_backups: list[tuple[Path, Path]] = []
    try:
        # Generate each skill
        for skill in skills:
            if skill.name == CORE_SKILL_NAME:
                generate_core_skill(stage_root / skill.name)
            else:
                generate_portable_skill(skill, stage_root / skill.name)

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
    except Exception as installation_error:
        rollback_errors: list[str] = []
        for destination in reversed(installed_destinations):
            try:
                if destination.exists() or destination.is_symlink():
                    remove_destination(destination)
            except Exception as error:
                rollback_errors.append(f"remove {destination}: {error}")
        for destination, backup in reversed(moved_backups):
            try:
                if backup.exists() or backup.is_symlink():
                    backup.rename(destination)
            except Exception as error:
                rollback_errors.append(
                    f"restore {backup} to {destination}: {error}"
                )
        if rollback_errors:
            preserve_backup = True
            details = "; ".join(rollback_errors)
            raise RuntimeError(
                "Engineering Power installation failed and rollback incomplete; "
                f"backups preserved at {backup_root}. Recovery errors: {details}"
            ) from installation_error
        raise
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)
        if backup_root is not None and not preserve_backup:
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
