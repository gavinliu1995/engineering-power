#!/usr/bin/env python3
"""Synchronize shared Engineering Power resources into the portable Skill."""

from __future__ import annotations

import argparse
from pathlib import Path
import filecmp
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_SKILLS_ROOT = ROOT / "skills"
PORTABLE_SKILLS_ROOT = ROOT / ".agents" / "skills"
PORTABLE_ROOT = PORTABLE_SKILLS_ROOT / "engineering-power"
RESOURCE_DIRECTORIES = {
    ROOT / "scripts" / "repo_evidence": PORTABLE_ROOT / "scripts" / "repo_evidence",
    ROOT / "references": PORTABLE_ROOT / "references",
}
EXCLUDED_PARTS = {"agents", "__pycache__"}
PORTABLE_RUNTIME = """\

## Portable runtime

This generated Agent Skill shares the adjacent `engineering-power` runtime core.
Resolve `$ENGINEERING_POWER_CORE` to `../engineering-power` relative to this
Skill directory. Run repository evidence tools from
`$ENGINEERING_POWER_CORE/scripts/repo_evidence/` and load shared report schemas
from `$ENGINEERING_POWER_CORE/references/`. Do not bypass the evidence engine
for repository, pull-request, comparison, working-tree, or patch analysis.
"""


def canonical_skill_directories() -> tuple[Path, ...]:
    return tuple(
        sorted(
            path
            for path in CANONICAL_SKILLS_ROOT.iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        )
    )


def included_file(path: Path, source: Path) -> bool:
    relative = path.relative_to(source)
    return (
        path.is_file()
        and not EXCLUDED_PARTS.intersection(relative.parts)
        and path.suffix != ".pyc"
    )


def transform_skill(content: str) -> str:
    transformed = content.replace("engineering-power:", "")
    transformed = transformed.replace("$PLUGIN_ROOT", "$ENGINEERING_POWER_CORE")
    transformed = transformed.replace(
        "../../references/",
        "../engineering-power/references/",
    )
    frontmatter_end = transformed.find("\n---", 4)
    if frontmatter_end < 0:
        raise ValueError("SKILL.md is missing closing YAML frontmatter")
    insertion_point = frontmatter_end + len("\n---")
    return (
        transformed[:insertion_point]
        + PORTABLE_RUNTIME
        + transformed[insertion_point:]
    )


def file_names(directory: Path) -> set[Path]:
    return {
        path.relative_to(directory)
        for path in directory.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }


def canonical_file_names(directory: Path) -> set[Path]:
    return {
        path.relative_to(directory)
        for path in directory.rglob("*")
        if included_file(path, directory)
    }


def differences(source: Path, destination: Path) -> list[str]:
    if not destination.is_dir():
        return [f"missing directory: {destination}"]

    source_files = file_names(source)
    destination_files = file_names(destination)
    result = [f"missing file: {destination / path}" for path in sorted(source_files - destination_files)]
    result.extend(f"unexpected file: {destination / path}" for path in sorted(destination_files - source_files))
    for relative_path in sorted(source_files & destination_files):
        if not filecmp.cmp(source / relative_path, destination / relative_path, shallow=False):
            result.append(f"different file: {destination / relative_path}")
    return result


def generated_skill_differences(source: Path, destination: Path) -> list[str]:
    if not destination.is_dir():
        return [f"missing directory: {destination}"]

    source_files = canonical_file_names(source)
    destination_files = file_names(destination)
    result = [
        f"missing file: {destination / path}"
        for path in sorted(source_files - destination_files)
    ]
    result.extend(
        f"unexpected file: {destination / path}"
        for path in sorted(destination_files - source_files)
    )
    for relative_path in sorted(source_files & destination_files):
        destination_path = destination / relative_path
        if relative_path == Path("SKILL.md"):
            expected = transform_skill(
                (source / relative_path).read_text(encoding="utf-8")
            )
            if destination_path.read_text(encoding="utf-8") != expected:
                result.append(f"different file: {destination_path}")
        elif not filecmp.cmp(
            source / relative_path,
            destination_path,
            shallow=False,
        ):
            result.append(f"different file: {destination_path}")
    return result


def copy_generated_skill(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    for source_path in source.rglob("*"):
        if not included_file(source_path, source):
            continue
        relative_path = source_path.relative_to(source)
        destination_path = destination / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        if relative_path == Path("SKILL.md"):
            destination_path.write_text(
                transform_skill(source_path.read_text(encoding="utf-8")),
                encoding="utf-8",
            )
        else:
            shutil.copy2(source_path, destination_path)


def remove_stale_generated_skills() -> None:
    expected = {path.name for path in canonical_skill_directories()}
    for candidate in PORTABLE_SKILLS_ROOT.iterdir():
        if (
            not candidate.is_dir()
            or candidate.name == "engineering-power"
            or candidate.name in expected
        ):
            continue
        skill_file = candidate / "SKILL.md"
        if (
            skill_file.is_file()
            and "## Portable runtime" in skill_file.read_text(encoding="utf-8")
        ):
            shutil.rmtree(candidate)


def sync() -> None:
    remove_stale_generated_skills()
    for source, destination in RESOURCE_DIRECTORIES.items():
        if destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            source,
            destination,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    for source in canonical_skill_directories():
        copy_generated_skill(source, PORTABLE_SKILLS_ROOT / source.name)


def suite_differences() -> list[str]:
    canonical = canonical_skill_directories()
    expected_directories = {path.name for path in canonical} | {"engineering-power"}
    actual_directories = {
        path.name
        for path in PORTABLE_SKILLS_ROOT.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }
    result = [
        f"missing portable skill directory: {PORTABLE_SKILLS_ROOT / name}"
        for name in sorted(expected_directories - actual_directories)
    ]
    result.extend(
        f"unexpected portable skill directory: {PORTABLE_SKILLS_ROOT / name}"
        for name in sorted(actual_directories - expected_directories)
    )
    result.extend(
        problem
        for source, destination in RESOURCE_DIRECTORIES.items()
        for problem in differences(source, destination)
    )
    result.extend(
        problem
        for source in canonical
        for problem in generated_skill_differences(
            source,
            PORTABLE_SKILLS_ROOT / source.name,
        )
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize or verify the self-contained portable Agent Skill."
    )
    parser.add_argument("--check", action="store_true", help="Fail if the package is stale.")
    arguments = parser.parse_args()

    if arguments.check:
        problems = suite_differences()
        if problems:
            print("portable Agent Skill suite is out of sync:", file=sys.stderr)
            print("\n".join(problems), file=sys.stderr)
            return 1
        print("portable Agent Skill suite is in sync")
        return 0

    sync()
    print(
        f"synchronized {len(canonical_skill_directories()) + 1} portable Agent Skills "
        f"at {PORTABLE_SKILLS_ROOT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
