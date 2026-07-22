#!/usr/bin/env python3
"""Synchronize shared Engineering Power resources into the portable Skill."""

from __future__ import annotations

import argparse
from pathlib import Path
import filecmp
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
PORTABLE_ROOT = ROOT / ".agents" / "skills" / "engineering-power"
RESOURCE_DIRECTORIES = {
    ROOT / "scripts" / "repo_evidence": PORTABLE_ROOT / "scripts" / "repo_evidence",
    ROOT / "references": PORTABLE_ROOT / "references",
}


def file_names(directory: Path) -> set[Path]:
    return {
        path.relative_to(directory)
        for path in directory.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
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


def sync() -> None:
    for source, destination in RESOURCE_DIRECTORIES.items():
        if destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            source,
            destination,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize or verify the self-contained portable Agent Skill."
    )
    parser.add_argument("--check", action="store_true", help="Fail if the package is stale.")
    arguments = parser.parse_args()

    if arguments.check:
        problems = [
            problem
            for source, destination in RESOURCE_DIRECTORIES.items()
            for problem in differences(source, destination)
        ]
        if problems:
            print("portable Agent Skill is out of sync:", file=sys.stderr)
            print("\n".join(problems), file=sys.stderr)
            return 1
        print("portable Agent Skill is in sync")
        return 0

    sync()
    print(f"synchronized portable Agent Skill at {PORTABLE_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
