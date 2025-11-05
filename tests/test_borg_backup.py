from pathlib import Path

import pytest

from src.borg_backup import Borg
from tests.utilities.utilities import compare_directories, to_archive_path


def test_create_repository(tmp_path):
    borg = Borg()

    repository = borg.create_repository(tmp_path, "repo")

    # We can safely assume the repository is a file repository
    repository_path = Path(repository)

    # Borg repositories contain a "config" file after initialization
    assert (repository_path / "config").exists()

    # Newly created repo should have no archives yet
    archives = borg.list_archives(repository)
    assert archives == []


def test_create_repository_fails_if_parent_missing(borg):
    with pytest.raises(RuntimeError, match=r"Parent directory does not exist"):
        borg.create_repository(Path("no_such_parent"), "repo")


def test_archive_fails_if_repository_missing(borg, testdata_dir):
    with pytest.raises(RuntimeError, match=r"does not exist"):
        borg.archive("no_such_repo", [testdata_dir])


def test_archive_fails_if_source_directory_missing(borg):
    with pytest.raises(RuntimeError, match=r"Source directory does not exist"):
        borg.archive("ignored", [Path("no_such_directory")])


def test_archive_and_restore(tmp_path, borg, repository, testdata_dir):
    # Target directory must exist for this test
    target_dir = tmp_path / "restore_here"
    target_dir.mkdir()

    archive = borg.archive(repository, [testdata_dir])

    # Source directories will be made relative for safety (to ensure restoring into target dir)
    borg.restore(
        repository,
        archive,
        [testdata_dir],
        target_dir
    )

    compare_directories(testdata_dir, target_dir / testdata_dir.relative_to("/"))


def test_restore_fails_if_repository_missing(borg):
    with pytest.raises(RuntimeError, match=r"does not exist"):
        borg.restore(
            repository="no_such_repo",
            archive="ignored",
            source_dirs=[Path("ignored")],
            target_dir=Path("ignored"),
        )


def test_restore_fails_if_archive_missing(borg, repository):
    with pytest.raises(RuntimeError, match=r"Archive does not exist"):
        borg.restore(
            repository=repository,
            archive="no_such_archive",
            source_dirs=[Path("ignored")],
            target_dir=Path("ignored"),
        )


def test_restore_fails_if_source_directory_not_in_archive(tmp_path, borg, repository, testdata_dir):
    target_dir = tmp_path / "restore_here"
    target_dir.mkdir()
    archive = borg.archive(repository=repository, source_dirs=[testdata_dir])

    with pytest.raises(RuntimeError, match="never matched"):
        borg.restore(
            repository=repository,
            archive=archive,
            source_dirs=[Path("no_such_directory")],
            target_dir=target_dir,
        )


def test_restore_fails_if_target_directory_missing(borg, repository, testdata_dir):
    archive = borg.archive(repository, [testdata_dir])

    with pytest.raises(RuntimeError, match=r"Target directory does not exist"):
        borg.restore(
            repository=repository,
            archive=archive,
            source_dirs=[testdata_dir],
            target_dir=Path("no_such_directory"),
        )


def test_list_contents_of_archive_with_testdata(tmp_path, project_root, borg, repository, testdata_dir):
    archive = borg.archive(repository=repository, source_dirs=[testdata_dir])

    paths = borg.list_contents(repository=repository, archive=archive)

    assert to_archive_path(testdata_dir) in paths
    assert to_archive_path(testdata_dir / "some directory") in paths
    assert to_archive_path(testdata_dir / "some file.txt") in paths
