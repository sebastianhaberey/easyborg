from __future__ import annotations

import filecmp
from datetime import datetime
from pathlib import Path
from typing import Any


def compare_directories(dir1: Path, dir2: Path):
    """
    Recursively compare two directories.
    Raises AssertionError if any difference is found.
    """
    comparison = filecmp.dircmp(dir1, dir2)
    assert not comparison.left_only, f"Missing items in {dir2}: {comparison.left_only}"
    assert (
        not comparison.right_only
    ), f"Unexpected items in {dir2}: {comparison.right_only}"
    assert (
        not comparison.diff_files
    ), f"Different file contents: {comparison.diff_files}"

    for common_dir in comparison.common_dirs:
        compare_directories(dir1 / common_dir, dir2 / common_dir)


def to_archive_path(p: Path) -> Path:
    """Convert an absolute filesystem Path to Borg list() relative form."""
    return Path(p.as_posix().lstrip("/"))


def to_archive_ref(repository: str, archive_name: str) -> str:
    return f"{repository}::{archive_name}"


def create_archive_name() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge two dicts. Values in override replace those in base."""
    result = dict(base)  # copy
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
