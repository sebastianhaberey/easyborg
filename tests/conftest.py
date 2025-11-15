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
def testdata_dir(project_root):
    return project_root / "tests" / "resources" / "testdata"
