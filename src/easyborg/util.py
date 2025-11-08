from __future__ import annotations

import filecmp
import secrets
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


def to_relative_path(p: Path) -> Path:
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
