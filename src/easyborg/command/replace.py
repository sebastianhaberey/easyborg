import shutil
from pathlib import Path

from easyborg import ui
from easyborg.fzf import Fzf
from easyborg.model import Config
from easyborg.util import relativize


class ReplaceCommand:
    def __init__(self, *, config: Config, fzf: Fzf):
        super().__init__()
        self.config = config
        self.fzf = fzf

    def run(self, *, dry_run: bool = False) -> None:
        """
        Replace configured folders with the versions located in the current working directory.
        """

        backup_folders = self.config.backup_folders
        cwd = Path.cwd()

        matching_folders = []
        for backup_folder in backup_folders:
            if (cwd / relativize(backup_folder)).exists():
                matching_folders.append(backup_folder)

        if not matching_folders:
            ui.error("No folders in the current directory match the configured backup folders.")
            return

        ui.selected("Select folders to replace")
        selected_folders = self.fzf.select_items(
            matching_folders,
            str,
            multi=True,
        )
        if not selected_folders:
            ui.warn("Aborted")
            return

        ui.newline()
        for folder in selected_folders:
            dst = folder
            ui.info(f"[cyan]{dst}[/cyan]")
        ui.newline()

        if len(selected_folders) > 1:
            ui.info("Replace these folders?")
        else:
            ui.info("Replace this folder?")
        confirm = self.fzf.confirm()
        if not confirm:
            ui.warn("Aborted")
            return

        for folder in selected_folders:
            dst = folder
            src = relativize(folder)

            ui.info(f"Replacing {dst}")

            if not dry_run:
                shutil.rmtree(dst)
                shutil.move(src, dst)

        ui.newline()
        ui.success("Replace complete")
