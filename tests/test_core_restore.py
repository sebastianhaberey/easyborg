# tests/test_core_restore.py
import os
from pathlib import Path

from tests.helpers.fakes import FakeFzf

from easyborg.core import Core
from easyborg.model import Config, RepositoryType, Snapshot
from easyborg.util import to_relative_path


def test_core_backup(tmp_path, testdata_dir, borg):
    """
    End-to-end: Core.backup() creates snapshot in backup repository.
    """

    repo_parent = tmp_path / "repos"
    repo_parent.mkdir()

    backup_repo = borg.create_repository(repo_parent, "backup", RepositoryType.BACKUP)
    archive_repo = borg.create_repository(repo_parent, "archive", RepositoryType.ARCHIVE)

    config = Config(
        source=tmp_path,
        folders=[testdata_dir],
        repos={"backup": backup_repo, "archive": archive_repo},
    )

    core = Core(config, borg=borg, compact_probability=1.0)
    core.backup()

    snapshots = borg.list_snapshots(archive_repo)
    assert len(snapshots) == 0

    snapshots = borg.list_snapshots(backup_repo)
    assert len(snapshots) == 1

    snapshot = snapshots[0]
    assert snapshot.repository.name == "backup"
    assert snapshot.name

    contents = list(borg.list_contents(snapshot))

    relative_testdata_dir = to_relative_path(testdata_dir)

    assert relative_testdata_dir in contents
    assert relative_testdata_dir / "file 1.txt" in contents
    assert relative_testdata_dir / "file 2.txt" in contents
    assert relative_testdata_dir / "some folder" in contents


def test_core_backup_multiple_repos(tmp_path, testdata_dir, borg):
    """
    End-to-end: Core.backup() creates snapshot in in multiple backup repositories.
    """

    repo_parent = tmp_path / "repos"
    repo_parent.mkdir()

    backup1_repo = borg.create_repository(repo_parent, "backup1", RepositoryType.BACKUP)
    backup2_repo = borg.create_repository(repo_parent, "backup2", RepositoryType.BACKUP)

    config = Config(
        source=tmp_path,
        folders=[testdata_dir],
        repos={"backup1": backup1_repo, "backup2": backup2_repo},
    )

    core = Core(config, borg=borg, compact_probability=1.0)
    core.backup()

    snapshots = borg.list_snapshots(backup1_repo)
    assert len(snapshots) == 1

    snapshots = borg.list_snapshots(backup2_repo)
    assert len(snapshots) == 1


def test_core_archive(tmp_path, testdata_dir, borg):
    """
    End-to-end: Core.archive() creates snapshot in archive repository.
    """

    repo_parent = tmp_path / "repos"
    repo_parent.mkdir()

    backup_repo = borg.create_repository(repo_parent, "backup", RepositoryType.BACKUP)
    archive_repo = borg.create_repository(repo_parent, "archive", RepositoryType.ARCHIVE)

    config = Config(
        source=tmp_path,
        folders=[testdata_dir],
        repos={"backup": backup_repo, "archive": archive_repo},
    )

    core = Core(config, borg=borg, compact_probability=1.0)

    some_folder = testdata_dir / "some folder"
    core.archive(some_folder)

    snapshots = borg.list_snapshots(backup_repo)
    assert len(snapshots) == 0

    snapshots = borg.list_snapshots(archive_repo)
    assert len(snapshots) == 1

    snapshot = snapshots[0]
    assert snapshot.repository.name == "archive"
    assert snapshot.name

    # Verify that the archived snapshot contains the expected files/folders
    contents = list(borg.list_contents(snapshot))

    # assert to_relative_path(some_folder)
    # assert to_relative_path(some_folder) / "nested.txt" in contents

    relative_testdata_dir = to_relative_path(testdata_dir)

    assert relative_testdata_dir / "some folder" in contents
    assert relative_testdata_dir / "some folder" / "nested.txt" in contents
    assert relative_testdata_dir / "file 1.txt" not in contents
    assert relative_testdata_dir / "file 2.txt" not in contents


def test_core_archive_multiple_repos(tmp_path, testdata_dir, borg):
    """
    End-to-end: Core.archive() creates snapshot in multiple archive repositories.
    """

    repo_parent = tmp_path / "repos"
    repo_parent.mkdir()

    archive1_repo = borg.create_repository(repo_parent, "archive1", RepositoryType.ARCHIVE)
    archive2_repo = borg.create_repository(repo_parent, "archive2", RepositoryType.ARCHIVE)

    config = Config(
        source=tmp_path,
        folders=[testdata_dir],
        repos={"archive1": archive1_repo, "archive2": archive2_repo},
    )

    core = Core(config, borg=borg, compact_probability=1.0)
    core.archive(testdata_dir)

    snapshots = borg.list_snapshots(archive1_repo)
    assert len(snapshots) == 1

    snapshots = borg.list_snapshots(archive2_repo)
    assert len(snapshots) == 1


def test_core_restore(tmp_path, borg, repo, testdata_dir):
    """
    End-to-end: Core.restore() restores snapshot from repository.
    """
    snap = Snapshot(repo, "snap1")
    borg.create_snapshot(snap, [testdata_dir])

    # Inject controlled user selections:
    # 1. Select the repo "repo"
    # 2. Select the snapshot "snap1"
    fzf = FakeFzf([repo, snap])

    config = Config(
        source=testdata_dir,
        repos={"repo": repo},
        folders=[testdata_dir],
    )

    core = Core(config, borg=borg, fzf=fzf)

    target_dir = tmp_path / "restore-target"
    target_dir.mkdir()
    cwd = Path.cwd()

    try:
        os.chdir(target_dir)
        core.restore()
    finally:
        os.chdir(cwd)

    # Verify restore result
    restored = target_dir / to_relative_path(testdata_dir)
    assert (restored / "file 1.txt").exists()
    assert (restored / "file 2.txt").exists()
    assert (restored / "some folder" / "nested.txt").exists()


def test_core_extract(tmp_path, borg, repo, testdata_dir):
    """
    End-to-end: Core.extract() extracts selected items (not the full snapshot).
    """

    # Create a snapshot to extract from
    snap = Snapshot(repo, "snap1", comment="Test-Snapshot")
    borg.create_snapshot(snap, [testdata_dir])

    # Simulate interactive user selections:
    # 1. Select the repo "repo"
    # 2. Select the snapshot "snap1"
    # 3. Select a subdirectory or file to extract
    selected_path = to_relative_path(testdata_dir) / "some folder"
    fzf = FakeFzf([repo, snap, selected_path])

    config = Config(
        source=testdata_dir,
        repos={"repo": repo},
        folders=[testdata_dir],
    )

    core = Core(config, borg=borg, fzf=fzf)

    target_dir = tmp_path / "extract-target"
    target_dir.mkdir()
    cwd = Path.cwd()

    try:
        os.chdir(target_dir)
        core.extract()
    finally:
        os.chdir(cwd)

    extracted_folder = target_dir / selected_path
    assert extracted_folder.exists()
    assert (extracted_folder / "nested.txt").exists()

    assert not (target_dir / to_relative_path(testdata_dir) / "file 1.txt").exists()
