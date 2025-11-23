import os
from pathlib import Path

from easyborg.command.extract import ExtractCommand
from easyborg.model import Config, Snapshot
from easyborg.util import relativize
from tests.helpers.fakes import FakeFzf


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
    selected_path = relativize(testdata_dir) / "some folder"
    fzf = FakeFzf([[repo], [snap], [selected_path]])

    config = Config(
        repos={"repo": repo},
        backup_folders=[testdata_dir],
    )

    target_dir = tmp_path / "extract-target"
    target_dir.mkdir()
    cwd = Path.cwd()

    try:
        os.chdir(target_dir)
        ExtractCommand(config=config, borg=borg, fzf=fzf).run()
    finally:
        os.chdir(cwd)

    extracted_folder = target_dir / selected_path
    assert extracted_folder.exists()
    assert (extracted_folder / "nested.txt").exists()

    assert not (target_dir / relativize(testdata_dir) / "file 1.txt").exists()
