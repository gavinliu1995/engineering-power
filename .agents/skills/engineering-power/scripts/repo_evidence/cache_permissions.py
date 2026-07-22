#!/usr/bin/env python3
"""Private-by-default permissions for collected repository evidence."""

import os
from pathlib import Path
import stat


PRIVATE_DIRECTORY_MODE = 0o700
PRIVATE_FILE_MODE = 0o600


def secure_directory(path):
    path = Path(path)
    if path.is_symlink():
        raise RuntimeError(f"Refusing to secure symlinked directory: {path}")
    path.chmod(PRIVATE_DIRECTORY_MODE)
    return path


def secure_file(path):
    path = Path(path)
    if path.is_symlink():
        raise RuntimeError(f"Refusing to secure symlinked file: {path}")
    path.chmod(PRIVATE_FILE_MODE)
    return path


def secure_tree(root):
    """Secure one tree without following or modifying symbolic links."""
    root = Path(root).expanduser()
    if root.is_symlink():
        raise RuntimeError(f"Refusing to secure symlinked cache root: {root}")
    if not root.exists():
        return {"directories": 0, "files": 0, "symlinks_skipped": 0}
    if not root.is_dir():
        raise RuntimeError(f"Cache root is not a directory: {root}")

    directories_secured = 1
    files_secured = 0
    symlinks_skipped = 0
    secure_directory(root)
    for current, directories, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        retained_directories = []
        for name in directories:
            path = current_path / name
            if path.is_symlink():
                symlinks_skipped += 1
                continue
            secure_directory(path)
            directories_secured += 1
            retained_directories.append(name)
        directories[:] = retained_directories
        for name in files:
            path = current_path / name
            if path.is_symlink():
                symlinks_skipped += 1
                continue
            secure_file(path)
            files_secured += 1
    return {
        "directories": directories_secured,
        "files": files_secured,
        "symlinks_skipped": symlinks_skipped,
    }


def audit_tree(root):
    """Return permission drift without following symbolic links."""
    root = Path(root).expanduser()
    if root.is_symlink():
        raise RuntimeError(f"Refusing to audit symlinked cache root: {root}")
    result = {
        "cache_root": str(root.resolve()),
        "exists": root.is_dir(),
        "directories_checked": 0,
        "files_checked": 0,
        "symlinks_skipped": 0,
        "insecure_entries": 0,
        "issues": [],
    }
    if not root.exists():
        return result
    if not root.is_dir():
        raise RuntimeError(f"Cache root is not a directory: {root}")

    def inspect(path, expected, kind, counter):
        actual = stat.S_IMODE(path.lstat().st_mode)
        result[counter] += 1
        if actual != expected:
            result["issues"].append(
                {
                    "path": str(path.resolve()),
                    "kind": kind,
                    "actual_mode": f"{actual:03o}",
                    "expected_mode": f"{expected:03o}",
                }
            )

    inspect(root, PRIVATE_DIRECTORY_MODE, "directory", "directories_checked")
    for current, directories, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        retained_directories = []
        for name in directories:
            path = current_path / name
            if path.is_symlink():
                result["symlinks_skipped"] += 1
                continue
            inspect(path, PRIVATE_DIRECTORY_MODE, "directory", "directories_checked")
            retained_directories.append(name)
        directories[:] = retained_directories
        for name in files:
            path = current_path / name
            if path.is_symlink():
                result["symlinks_skipped"] += 1
                continue
            inspect(path, PRIVATE_FILE_MODE, "file", "files_checked")
    result["insecure_entries"] = len(result["issues"])
    return result
