import os
import shutil
from typing import Any

from easyborg.command.replace import ReplaceCommand
from easyborg.model import Config
from easyborg.util import relativize
from tests.helpers.fakes import FakeFzf


def test_replace_command(tmp_path, monkeypatch):
    try:
        os.chdir(tmp_path)

        existing_file = tmp_path / "test.txt"  # /temporary/dir/test.txt
        existing_file.write_text("EXISTING")

        restore_dir = relativize(tmp_path)  # temporary/dir (inside /temporary/dir)
        restore_dir.mkdir(parents=True)
        restore_file = restore_dir / "test.txt"  # temporary/dir/test.txt
        restore_file.write_text("RESTORED")

        # Configure the existing file as backup path
        config = Config(backup_paths=[existing_file], repos={})

        # 1) select the backup path
        # 2) confirm "Replace?"
        fzf = FakeFzf(responses=[[existing_file], ["YES"]])

        # Mock the two dangerous operations
        calls: dict[str, Any] = {"rmtree": None, "move": None}

        def fake_rmtree(path):
            calls["rmtree"] = path

        def fake_move(src, dst):
            calls["move"] = (src, dst)

        monkeypatch.setattr(shutil, "rmtree", fake_rmtree)
        monkeypatch.setattr(shutil, "move", fake_move)

        cmd = ReplaceCommand(config=config, fzf=fzf)
        cmd.run()
    finally:
        os.chdir(tmp_path)

    assert calls["rmtree"] == existing_file
    assert calls["move"] == (restore_file, existing_file)
