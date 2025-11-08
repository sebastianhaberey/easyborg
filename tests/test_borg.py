from pathlib import Path

import pytest

from easyborg.borg import Borg
from easyborg.model import Repository, RepositoryType, Snapshot
from easyborg.util import compare_directories, to_relative_path


def test_create_repository(tmp_path):
    borg = Borg()

    repo = borg.create_repository(tmp_path, "repo")
    repo_path = Path(repo.url)

    assert (repo_path / "config").exists()
    assert borg.list_snapshots(repo) == []


def test_create_repository_fails_if_parent_directory_not_found(borg):
    with pytest.raises(RuntimeError, match=r"Parent directory does not exist"):
        borg.create_repository(Path("foo"), "repo")


def test_create_snapshot_fails_if_repository_not_found(borg, testdata_dir):
    fake_repo = Repository(name="foo", url="bar", type=RepositoryType.BACKUP)
    snap = Snapshot(fake_repo, "baz")

    with pytest.raises(RuntimeError):
        borg.create_snapshot(snap, [testdata_dir])


def test_create_snapshot_fails_if_folder_not_found(borg, repository):
    snap = Snapshot(repository, "ignored")

    with pytest.raises(RuntimeError, match=r"Folder does not exist"):
        borg.create_snapshot(snap, [Path("foo")])


def test_create_snapshot_and_restore_single(tmp_path, borg, repository, testdata_dir):
    snap = Snapshot(repository, "snapshot")
    borg.create_snapshot(snap, [testdata_dir])

    target_dir = tmp_path / "target"
    target_dir.mkdir()

    borg.restore(snap, target_dir, folders=[testdata_dir / "file 1.txt"])

    file_1 = target_dir / to_relative_path(testdata_dir) / "file 1.txt"
    assert file_1.exists()

    file_2 = target_dir / to_relative_path(testdata_dir) / "file 2.txt"
    assert not file_2.exists()


def test_create_snapshot_and_restore_all(tmp_path, borg, repository, testdata_dir):
    snap = Snapshot(repository, "snapshot")
    borg.create_snapshot(snap, [testdata_dir])

    target_dir = tmp_path / "target"
    target_dir.mkdir()

    borg.restore(snap, target_dir)

    compare_directories(testdata_dir, target_dir / to_relative_path(testdata_dir))


def test_restore_fails_if_target_directory_not_found(borg, repository, testdata_dir):
    snap = Snapshot(repository, "snapshot")
    borg.create_snapshot(snap, [testdata_dir])

    with pytest.raises(RuntimeError, match=r"Target directory does not exist"):
        borg.restore(snap, Path("foo"), folders=[testdata_dir])


def test_restore_fails_if_folder_not_found(tmp_path, borg, repository, testdata_dir):
    snap = Snapshot(repository, "snapshot")
    borg.create_snapshot(snap, [testdata_dir])

    target_dir = tmp_path / "restore_here"
    target_dir.mkdir()

    with pytest.raises(RuntimeError, match=r"(?i)never matched"):
        borg.restore(snap, target_dir, folders=[Path("foo")])


def test_list_contents_of_snapshot_with_testdata(borg, repository, testdata_dir):
    snap = Snapshot(repository, "snapshot")
    borg.create_snapshot(snap, [testdata_dir])

    paths = list(borg.list_contents(snap))

    assert to_relative_path(testdata_dir) in paths
    assert to_relative_path(testdata_dir / "some folder") in paths
    assert to_relative_path(testdata_dir / "file 1.txt") in paths


def test_list_contents_fails_if_repository_not_found(borg):
    fake_repo = Repository(name="foo", url="bar", type=RepositoryType.BACKUP)
    snap = Snapshot(fake_repo, "baz")

    with pytest.raises(RuntimeError):
        list(borg.list_contents(snap))


def test_list_contents_fails_if_snapshot_not_found(borg, repository):
    snap = Snapshot(repository, "foo")

    with pytest.raises(RuntimeError):
        list(borg.list_contents(snap))
