from easyborg.command.archive import ArchiveCommand
from easyborg.model import Config, RepositoryType
from easyborg.util import relativize


def test_archive_command(tmp_path, testdata_dir, borg):
    """
    End-to-end: Core.archive() creates snapshot in archive repository.
    """

    repo_parent = tmp_path / "repos"
    repo_parent.mkdir()

    backup_repo = borg.create_repository(repo_parent, "backup", RepositoryType.BACKUP)
    archive_repo = borg.create_repository(repo_parent, "archive", RepositoryType.ARCHIVE)

    config = Config(
        backup_paths=[testdata_dir],
        repos={"backup": backup_repo, "archive": archive_repo},
    )

    some_folder = testdata_dir / "some folder"

    ArchiveCommand(config=config, borg=borg).run(some_folder)

    snapshots = borg.list_snapshots(backup_repo)
    assert len(snapshots) == 0

    snapshots = borg.list_snapshots(archive_repo)
    assert len(snapshots) == 1

    snapshot = snapshots[0]
    assert snapshot.repository.name == "archive"
    assert snapshot.name

    # Verify that the archived snapshot contains the expected paths
    contents = list(borg.list_contents(snapshot))

    relative_testdata_dir = relativize(testdata_dir)

    assert relative_testdata_dir / "some folder" in contents
    assert relative_testdata_dir / "some folder" / "nested.txt" in contents
    assert relative_testdata_dir / "file 1.txt" not in contents
    assert relative_testdata_dir / "file 2.txt" not in contents


def test_archive_command_multiple_repos(tmp_path, testdata_dir, borg):
    """
    End-to-end: Core.archive() creates snapshot in multiple archive repositories.
    """

    repo_parent = tmp_path / "repos"
    repo_parent.mkdir()

    archive1_repo = borg.create_repository(repo_parent, "archive1", RepositoryType.ARCHIVE)
    archive2_repo = borg.create_repository(repo_parent, "archive2", RepositoryType.ARCHIVE)

    config = Config(
        backup_paths=[testdata_dir],
        repos={"archive1": archive1_repo, "archive2": archive2_repo},
    )

    ArchiveCommand(config=config, borg=borg).run(testdata_dir)

    snapshots = borg.list_snapshots(archive1_repo)
    assert len(snapshots) == 1

    snapshots = borg.list_snapshots(archive2_repo)
    assert len(snapshots) == 1
