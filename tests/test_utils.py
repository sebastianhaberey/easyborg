from pathlib import Path

from easyborg.util import to_relative_path


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
