from pathlib import Path

import pytest

from easyborg.borg import Borg
from easyborg.util import compare_directories, to_relative_path


def test_create_repository(tmp_path):
    borg = Borg()

    repository = borg.create_repository(tmp_path, "repo")

    # We can safely assume the repository is a file repository
    repository_path = Path(repository)

    # Borg repositories contain a "config" file after initialization
    assert (repository_path / "config").exists()

    # Newly created repo should have no snapshots yet
    snapshots = borg.list_snapshots(repository)
    assert snapshots == []


def test_create_repository_fails_if_parent_missing(borg):
    with pytest.raises(RuntimeError, match=r"Parent directory does not exist"):
        borg.create_repository(Path("no_such_parent"), "repo")


def test_create_snapshot_fails_if_repository_missing(borg, testdata_dir):
    with pytest.raises(RuntimeError, match=r"does not exist"):
        borg.create_snapshot(repository="no_such_repo", snapshot="ignored", folders=[testdata_dir])


def test_create_snapshot_fails_if_source_directory_missing(borg):
    with pytest.raises(RuntimeError, match=r"Folder does not exist"):
        borg.create_snapshot(repository="ignored", snapshot="ignored", folders=[Path("no_such_folder")])


def test_create_snapshot_and_restore_single(tmp_path, borg, repository, testdata_dir):
    borg.create_snapshot(repository=repository, snapshot="snapshot", folders=[testdata_dir])

    target_dir = tmp_path / "restore_here"
    target_dir.mkdir()

    borg.restore(
        repository=repository, snapshot="snapshot", target_dir=target_dir, folders=[testdata_dir / "file 1.txt"]
    )

    file_1 = target_dir / to_relative_path(testdata_dir) / "file 1.txt"
    assert file_1.exists()

    file_2 = target_dir / to_relative_path(testdata_dir) / "file 2.txt"
    assert not file_2.exists()


def test_create_snapshot_and_restore_all(tmp_path, borg, repository, testdata_dir):
    borg.create_snapshot(repository=repository, snapshot="snapshot", folders=[testdata_dir])

    target_dir = tmp_path / "restore_here"
    target_dir.mkdir()

    borg.restore(repository=repository, snapshot="snapshot", target_dir=target_dir)

    compare_directories(testdata_dir, target_dir / to_relative_path(testdata_dir))


def test_restore_fails_if_repository_missing(borg):
    with pytest.raises(RuntimeError):
        borg.restore(
            repository="no_such_repo", snapshot="ignored", target_dir=Path("ignored"), folders=[Path("ignored")]
        )


def test_restore_fails_if_snapshot_missing(borg, repository):
    with pytest.raises(RuntimeError):
        borg.restore(
            repository=repository, snapshot="no_such_snapshot", target_dir=Path("ignored"), folders=[Path("ignored")]
        )


def test_restore_fails_if_folder_not_in_snapshot(tmp_path, borg, repository, testdata_dir):
    target_dir = tmp_path / "restore_here"
    target_dir.mkdir()

    borg.create_snapshot(repository=repository, snapshot="snapshot", folders=[testdata_dir])

    with pytest.raises(RuntimeError, match="(?i)never matched"):
        borg.restore(
            repository=repository, snapshot="snapshot", target_dir=target_dir, folders=[Path("no_such_folder")]
        )


def test_restore_fails_if_target_directory_missing(borg, repository, testdata_dir):
    borg.create_snapshot(repository, snapshot="snapshot", folders=[testdata_dir])

    with pytest.raises(RuntimeError, match=r"Target directory does not exist"):
        borg.restore(
            repository=repository, snapshot="snapshot", target_dir=Path("no_such_directory"), folders=[testdata_dir]
        )


def test_list_contents_of_snapshot_with_testdata(tmp_path, project_root, borg, repository, testdata_dir):
    borg.create_snapshot(repository=repository, snapshot="snapshot", folders=[testdata_dir])

    paths = list(borg.list_contents(repository=repository, snapshot="snapshot"))

    assert to_relative_path(testdata_dir) in paths
    assert to_relative_path(testdata_dir / "some folder") in paths
    assert to_relative_path(testdata_dir / "file 1.txt") in paths


def test_list_contents_fails_if_repository_missing(borg):
    with pytest.raises(RuntimeError):
        list(borg.list_contents(repository="no_such_repository", snapshot="ignored"))


def test_list_contents_fails_if_snapshot_missing(borg, repository):
    with pytest.raises(RuntimeError):
        list(borg.list_contents(repository=repository, snapshot="no_such_snapshot"))
