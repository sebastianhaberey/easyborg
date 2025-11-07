from __future__ import annotations

from pathlib import Path

from easyborg.config import Config


class Core:
    def __init__(self, config: Config):
        self.config = config
        self.repositories = config.repositories
        self.folders = config.folders

    def backup(self):
        pass # TODO: create snapshot of all configured folders in each repository of type "backup"

    def archive(self, folder: Path):
        pass # TODO: create snapshort of configured folder in each repository of type "archive"

    def restore(self, repo: str = None, snapshot: str = None, target_dir: str = None):
        pass # TODO: prompt user to select repo and snapshot, restore to current working directory
