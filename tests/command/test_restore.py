import os
from pathlib import Path

from easyborg.command.restore import RestoreCommand
from easyborg.model import Config, Snapshot
from easyborg.util import to_relative_path
from tests.helpers.fakes import FakeFzf


def test_core_restore(tmp_path, borg, repo, testdata_dir):
    """
    End-to-end: Core.restore() restores snapshot from repository.
    """
    snap = Snapshot(repo, "snap1")
    borg.create_snapshot(snap, [testdata_dir])

    # Inject controlled user selections:
    # 1. Select the repo "repo"
    # 2. Select the snapshot "snap1"
    fzf = FakeFzf([[repo], [snap]])

    config = Config(
        repos={"repo": repo},
        backup_folders=[testdata_dir],
    )

    target_dir = tmp_path / "restore-target"
    target_dir.mkdir()
    cwd = Path.cwd()

    try:
        os.chdir(target_dir)
        RestoreCommand(config=config, borg=borg, fzf=fzf).run()
    finally:
        os.chdir(cwd)

    # Verify restore result
    restored = target_dir / to_relative_path(testdata_dir)
    assert (restored / "file 1.txt").exists()
    assert (restored / "file 2.txt").exists()
    assert (restored / "some folder" / "nested.txt").exists()
