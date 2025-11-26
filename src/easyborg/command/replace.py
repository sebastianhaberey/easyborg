import shutil
from pathlib import Path

from easyborg import ui
from easyborg.fzf import Fzf
from easyborg.interaction import confirm, select_paths
from easyborg.model import Config
from easyborg.util import relativize


class ReplaceCommand:
    def __init__(self, *, config: Config, fzf: Fzf):
        super().__init__()
        self.config = config
        self.fzf = fzf

    def run(self, *, dry_run: bool = False) -> None:
        backup_paths = self.config.backup_paths
        if not backup_paths:
            ui.warn("No backup paths configured")
            return

        cwd = Path.cwd()

        matching_paths: list[Path] = []
        for backup_path in backup_paths:
            if (cwd / relativize(backup_path)).exists():
                matching_paths.append(backup_path)

        if not matching_paths:
            ui.error("No items in the current directory match the configured backup paths.")
            return

        selected_paths = select_paths(self.fzf, matching_paths)
        if not selected_paths:
            ui.abort()
            return

        response = confirm(self.fzf, "Replace? ", danger=True)
        if not response:
            ui.abort()
            return

        ui.newline()

        for path in selected_paths:
            dst = path
            src = relativize(path)

            ui.info(f"Replacing {dst}")

            if not dry_run:
                shutil.rmtree(dst)
                shutil.move(src, dst)

        ui.success("Replace complete")
