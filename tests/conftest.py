from pathlib import Path

import pytest

from easyborg.borg import Borg
from easyborg.model import RepositoryType


@pytest.fixture
def project_root():
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def borg():
    return Borg()


@pytest.fixture
def repo(borg, tmp_path):
    return borg.create_repository(tmp_path, "repo", RepositoryType.BACKUP)


@pytest.fixture
def testdata_dir(tmp_path):
    base = tmp_path / "testdata"
    base.mkdir()
    (base / "file 1.txt").write_text("foo")
    (base / "file 2.txt").write_text("bar")
    sub = base / "some folder"
    sub.mkdir()
    (sub / "nested.txt").write_text("baz")
    return base
