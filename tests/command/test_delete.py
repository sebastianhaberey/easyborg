from easyborg.command.delete import DeleteCommand
from easyborg.model import Config, Snapshot
from tests.helpers.fakes import FakeFzf


def test_core_backup(tmp_path, borg, repo, testdata_dir):
    """
    End-to-end: Core.delete() removes snapshot from repository.
    """

    # Create a snapshot to delete
    snap = Snapshot(repo, "snap1", comment="Test-Snapshot")
    borg.create_snapshot(snap, [testdata_dir])

    snapshots = borg.list_snapshots(repo)
    assert len(snapshots) == 1

    # Simulate interactive user selections:
    # 1. Select the repo "repo"
    # 2. Select the snapshot "snap1"
    # 3. Confirm "YES"
    fzf = FakeFzf([[repo], [snap], ["YES"]])

    config = Config(
        repos={"repo": repo},
        backup_folders=[],  # not needed for delete
    )

    DeleteCommand(config=config, borg=borg, fzf=fzf).run()

    snapshots = borg.list_snapshots(repo)
    assert len(snapshots) == 0
