# tests/test_core.py
from unittest.mock import Mock

from easyborg.command.backup import BackupCommand
from easyborg.model import Config, Repository, RepositoryType
from easyborg.util import relativize


def test_core_backup(tmp_path, testdata_dir, borg):
    """
    End-to-end: Core.backup() creates snapshot in backup repository.
    """

    repo_parent = tmp_path / "repos"
    repo_parent.mkdir()

    backup_repo = borg.create_repository(repo_parent, "backup", RepositoryType.BACKUP)
    archive_repo = borg.create_repository(repo_parent, "archive", RepositoryType.ARCHIVE)

    config = Config(
        backup_paths=[testdata_dir],
        repos={"backup": backup_repo, "archive": archive_repo},
    )

    BackupCommand(config=config, borg=borg).run()

    snapshots = borg.list_snapshots(archive_repo)
    assert len(snapshots) == 0

    snapshots = borg.list_snapshots(backup_repo)
    assert len(snapshots) == 1

    snapshot = snapshots[0]
    assert snapshot.repository.name == "backup"
    assert snapshot.name

    contents = list(borg.list_contents(snapshot))

    relative_testdata_dir = relativize(testdata_dir)

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
        backup_paths=[testdata_dir],
        repos={"backup1": backup1_repo, "backup2": backup2_repo},
    )

    BackupCommand(config=config, borg=borg).run()

    snapshots = borg.list_snapshots(backup1_repo)
    assert len(snapshots) == 1

    snapshots = borg.list_snapshots(backup2_repo)
    assert len(snapshots) == 1


def test_core_backup_tenacious_mode(tmp_path, testdata_dir):
    """
    Tenacious mode: backup to first repo fails, backup to second repo succeeds.
    """

    repo_parent = tmp_path / "repos"
    repo_parent.mkdir()

    backup1_repo = Repository(url="foo", name="foo", type=RepositoryType.BACKUP)
    backup2_repo = Repository(url="bar", name="bar", type=RepositoryType.BACKUP)

    config = Config(
        backup_paths=[testdata_dir],
        repos={"backup1": backup1_repo, "backup2": backup2_repo},
    )

    borg = Mock()

    # create_snapshot: fail first time, succeed second time
    borg.create_snapshot.side_effect = [
        Exception("boom"),
        None,
    ]

    borg.prune.return_value = []
    borg.compact.return_value = []

    BackupCommand(config=config, borg=borg).run(tenacious=True)

    assert borg.create_snapshot.call_count == 2
