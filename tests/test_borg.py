from pathlib import Path

import pytest

from easyborg.model import Repository, RepositoryType, Snapshot
from easyborg.util import compare_directories, relativize


def test_create_repository(tmp_path, borg):
    repo = borg.create_repository(tmp_path, "repo", RepositoryType.BACKUP)
    repo_path = Path(repo.url)

    assert (repo_path / "config").exists()
    assert borg.list_snapshots(repo) == []


def test_create_repository_fails_if_parent_directory_not_found(borg):
    with pytest.raises(RuntimeError, match=r"Parent directory does not exist"):
        borg.create_repository(Path("foo"), "repo", RepositoryType.BACKUP)


def test_create_snapshot_fails_if_repository_not_found(borg, testdata_dir):
    fake_repo = Repository(name="foo", url="bar", type=RepositoryType.BACKUP)
    snap = Snapshot(fake_repo, "baz")

    with pytest.raises(RuntimeError):
        borg.create_snapshot(snap, [testdata_dir])


def test_create_snapshot_fails_if_path_not_found(borg, repo):
    snap = Snapshot(repo, "ignored")

    with pytest.raises(RuntimeError, match=r"Path does not exist"):
        borg.create_snapshot(snap, [Path("foo")])


def test_create_snapshot_and_restore_single(tmp_path, borg, repo, testdata_dir):
    snap = Snapshot(repo, "snapshot")
    borg.create_snapshot(snap, [testdata_dir])

    target_dir = tmp_path / "target"
    target_dir.mkdir()

    borg.restore(snap, target_dir, paths=[testdata_dir / "file 1.txt"])

    file_1 = target_dir / relativize(testdata_dir) / "file 1.txt"
    assert file_1.exists()

    file_2 = target_dir / relativize(testdata_dir) / "file 2.txt"
    assert not file_2.exists()


def test_create_snapshot_and_restore_all(tmp_path, borg, repo, testdata_dir):
    snap = Snapshot(repo, "snapshot")
    borg.create_snapshot(snap, [testdata_dir])

    target_dir = tmp_path / "target"
    target_dir.mkdir()

    borg.restore(snap, target_dir)

    compare_directories(testdata_dir, target_dir / relativize(testdata_dir))


def test_create_snapshot_with_comment(borg, repo, testdata_dir):
    comment = "This is a test comment"
    snap = Snapshot(repo, "snapshot", comment=comment)
    borg.create_snapshot(snap, [testdata_dir])

    snapshots = borg.list_snapshots(repo)
    matching = [s for s in snapshots if s.name == snap.name]

    assert len(matching), "Snapshot not found after creation"
    assert matching[0].comment == comment


def test_restore_fails_if_target_directory_not_found(borg, repo, testdata_dir):
    snap = Snapshot(repo, "snapshot")
    borg.create_snapshot(snap, [testdata_dir])

    with pytest.raises(RuntimeError, match=r"Target directory does not exist"):
        borg.restore(snap, Path("foo"))


def test_restore_fails_if_path_not_found(tmp_path, borg, repo, testdata_dir):
    snap = Snapshot(repo, "snapshot")
    borg.create_snapshot(snap, [testdata_dir])

    target_dir = tmp_path / "restore_here"
    target_dir.mkdir()

    with pytest.raises(RuntimeError, match=r"(?i)never matched"):
        borg.restore(snap, target_dir, paths=[Path("foo")])


def test_list_contents_of_snapshot_with_testdata(borg, repo, testdata_dir):
    snap = Snapshot(repo, "snapshot")
    borg.create_snapshot(snap, [testdata_dir])

    paths = list(borg.list_contents(snap))

    assert relativize(testdata_dir) in paths
    assert relativize(testdata_dir / "some folder") in paths
    assert relativize(testdata_dir / "file 1.txt") in paths


def test_list_contents_fails_if_repository_not_found(borg):
    fake_repo = Repository(name="foo", url="bar", type=RepositoryType.BACKUP)
    snap = Snapshot(fake_repo, "baz")

    with pytest.raises(RuntimeError):
        list(borg.list_contents(snap))


def test_list_contents_fails_if_snapshot_not_found(borg, repo):
    snap = Snapshot(repo, "foo")

    with pytest.raises(RuntimeError):
        list(borg.list_contents(snap))


def test_delete_snapshot(tmp_path, borg, repo, testdata_dir):
    snap = Snapshot(repo, "snapshot")
    borg.create_snapshot(snap, [testdata_dir])

    assert len(borg.list_snapshots(repo)) == 1

    borg.delete(snap)

    assert len(borg.list_snapshots(repo)) == 0


def test_delete_selected_snapshot_only(tmp_path, borg, repo, testdata_dir):
    snap1 = Snapshot(repo, "snapshot1")
    borg.create_snapshot(snap1, [testdata_dir])
    snap2 = Snapshot(repo, "snapshot2")
    borg.create_snapshot(snap2, [testdata_dir])

    assert len(borg.list_snapshots(repo)) == 2

    borg.delete(snap2)

    snapshots = borg.list_snapshots(repo)
    assert len(snapshots) == 1
    assert snapshots[0].name == snap1.name
