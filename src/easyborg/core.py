from __future__ import annotations

from easyborg import ui
from easyborg.config import Config


class Core:
    def __init__(self, config: Config):
        self.config = config
        self.repositories = config.repositories
        self.folders = config.folders

    def print_all(self):
        ui.info(f"Repositories: {list(self.repositories.keys())}")
        ui.warn(f"Folders: {[str(p) for p in self.folders]}")
        pass
