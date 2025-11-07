from pathlib import Path

import pytest

from easyborg.borg import Borg


@pytest.fixture
def project_root():
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def borg():
    return Borg()


@pytest.fixture
def repository(borg, tmp_path):
    return borg.create_repository(tmp_path, "repo")


@pytest.fixture
def testdata_dir(project_root):
    return project_root / "tests" / "resources" / "testdata"
