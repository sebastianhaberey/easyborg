from __future__ import annotations

from easyborg.config import Config


class Core:
    def __init__(self, config: Config):
        self.config = config
        self.repositories = config.repositories
        self.paths = config.paths

    def print_all(self):
        print(f"Repositories: {list(self.repositories.keys())}")
        print(f"Paths: {self.paths}")
        pass
