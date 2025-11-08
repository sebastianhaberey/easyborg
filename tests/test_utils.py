from datetime import datetime
from pathlib import Path

from easyborg.util import create_snapshot_name, to_relative_path


def test_to_relative_path_strips_leading_slash():
    p = Path("/Users/alice/Documents/file.txt")
    result = to_relative_path(p)
    assert result == Path("Users/alice/Documents/file.txt")
    assert not result.is_absolute()


def test_to_relative_path_keeps_relative_paths_unchanged():
    p = Path("relative/path/to/thing")
    result = to_relative_path(p)
    assert result == Path("relative/path/to/thing")
    assert not result.is_absolute()


def test_create_snapshot_name_format():
    when = datetime(2025, 2, 20, 14, 27, 9)
    name = create_snapshot_name(when)

    assert name.startswith("2025-02-20T14:27:09-")
    suffix = name.split("-")[-1]

    assert len(suffix) == 8
    assert all(c in "0123456789ABCDEF" for c in suffix)
