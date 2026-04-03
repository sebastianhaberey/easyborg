import os
import shutil
from typing import Any

from easyborg.command.replace import ReplaceCommand
from easyborg.model import Config
from easyborg.util import relativize
from tests.helpers.fakes import FakeFzf


def test_replace_command(tmp_path, testdata_dir, monkeypatch):
    """
    /tmp/pytest-16/
        source/
            tmp/pytest-16/target
                file 1.txt
                file 2.txt
                some folder/
        target/
            file 1.txt
            file 2.txt
            some folder/
    """
    source_dir = tmp_path / "source"
    target_dir = tmp_path / "target"

    target_dir_relative = relativize(target_dir)

    shutil.copytree(testdata_dir, source_dir / target_dir_relative)
    shutil.copytree(testdata_dir, target_dir)

    os.chdir(source_dir)

    # Configure the target dir as backup path
    config = Config(backup_paths=[target_dir], repos={})

    # 1) select the backup path
    # 2) confirm "Replace?"
    fzf = FakeFzf(responses=[[target_dir], ["YES"]])

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

    assert calls["rmtree"] == target_dir
    assert calls["move"] == (target_dir_relative, target_dir)


def test_replace_command_non_existing_target(tmp_path, testdata_dir, monkeypatch):
    """
    /tmp/pytest-16/
        source/
            tmp/pytest-16/target
                file 1.txt
                file 2.txt
                some folder/
    """
    source_dir = tmp_path / "source"
    target_dir = tmp_path / "target"

    target_dir_relative = relativize(target_dir)

    shutil.copytree(testdata_dir, source_dir / target_dir_relative)

    os.chdir(source_dir)

    # Configure the target dir as backup path
    config = Config(backup_paths=[target_dir], repos={})

    # 1) select the backup path
    # 2) confirm "Replace?"
    fzf = FakeFzf(responses=[[target_dir], ["YES"]])

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

    assert calls["rmtree"] is None
    assert calls["move"] == (target_dir_relative, target_dir)
