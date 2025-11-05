import filecmp
from pathlib import Path


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


def to_archive_path(p: Path) -> Path:
    """Convert an absolute filesystem Path to Borg list() relative form."""
    return Path(p.as_posix().lstrip("/"))
