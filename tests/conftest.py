from pathlib import Path

import pytest
from easyborg.borg import Borg
from easyborg.model import Repository, RepositoryType
from easyborg.process import get_full_executable_path


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def borg_executable_path() -> Path:
    return get_full_executable_path("borg")


@pytest.fixture
def borg(borg_executable_path: Path) -> Borg:
    return Borg(borg_executable_path)


@pytest.fixture
def repo(borg, tmp_path) -> Repository:
    return borg.create_repository(tmp_path, "repo", RepositoryType.BACKUP)


@pytest.fixture
def testdata_dir(project_root) -> Path:
    return project_root / "tests" / "resources" / "testdata"
