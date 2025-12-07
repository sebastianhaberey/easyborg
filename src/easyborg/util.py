from __future__ import annotations

import filecmp
import platform
import secrets
import subprocess
from datetime import datetime
from pathlib import Path

from easyborg.model import Snapshot


def compare_directories(dir1: Path, dir2: Path):
    """
    Recursively compare two directories.
    Raises AssertionError if any difference is found.
    """
    comparison = filecmp.dircmp(dir1, dir2)
    assert not comparison.left_only, f"Missing items in {dir2}: {comparison.left_only}"
    assert not comparison.right_only, f"Unexpected items in {dir2}: {comparison.right_only}"
    assert not comparison.diff_files, f"Different file contents: {comparison.diff_files}"

    for common_dir in comparison.common_dirs:
        compare_directories(dir1 / common_dir, dir2 / common_dir)


def relativize(p: Path) -> Path:
    """
    Convert a path to a relative path.
    Leading slashes are removed; relative paths are returned as-is.
    """
    return Path(p.as_posix().lstrip("/"))


def to_snapshot_ref(repository: str, snapshot: str) -> str:
    return f"{repository}::{snapshot}"


def create_snapshot_name(when: datetime | None = None) -> str:
    """
    Return a snapshot name of the form:

        YYYY-MM-DDTHH:MM:SS-XXXXXXXX

    where XXXXXXXX is an 8-character hex suffix (32 bits), providing extremely low collision probability.
    """
    if when is None:
        when = datetime.now().astimezone()

    timestamp = when.strftime("%Y-%m-%dT%H:%M:%S")
    suffix = secrets.token_hex(4).upper()  # 4 bytes → 8 hex chars

    return f"{timestamp}-{suffix}"


def find_snapshot_by_name(name: str, snapshots: list[Snapshot]) -> Snapshot | None:
    matching = next(s for s in snapshots if name.startswith(s.name))
    if matching is None:
        raise RuntimeError(f"Snapshot does not exist: {name}")
    return matching


def remove_redundant_paths(paths: list[Path]) -> list[Path]:
    """
    Normalize a list of Paths by removing redundant descendants.
    Preserves the input order.

    NOTE: complexity is about O(n^2) - dont use it on huge lists.
    """
    result: list[Path] = []

    for p in paths:
        # Skip if this path is already covered by an existing parent
        if any(p.is_relative_to(parent) for parent in result):
            continue

        # Remove existing children now that we have a better (higher) parent
        result = [parent for parent in result if not parent.is_relative_to(p)]

        # Add current path
        result.append(p)

    return result


def open_path(target: str | Path) -> None:
    """Open a file, folder, or URL using the system's default application."""
    target_str = str(target)

    system = platform.system()
    if system == "Darwin":
        cmd = ["open", target_str]
    elif system == "Linux":
        cmd = ["xdg-open", target_str]
    else:
        raise RuntimeError(f"Unsupported OS: {system}")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise FileNotFoundError(f"Failed to open {target_str!r}: {e}") from e


def is_blank(value: str | None) -> bool:
    return not (value and value.strip())
