import random
from pathlib import Path

from easyborg import ui
from easyborg.borg import Borg
from easyborg.model import Config, RepositoryType, Snapshot
from easyborg.util import create_snapshot_name


class ArchiveCommand:
    def __init__(self, *, config: Config, borg: Borg):
        super().__init__()
        self.config = config
        self.borg = borg

    def run(self, path: Path, *, dry_run: bool = False, comment: str | None = None) -> None:
        if not path.exists():
            raise RuntimeError(f"Path does not exist: {path}")

        index = 0
        for repo in self.config.repos.values():
            if repo.type is not RepositoryType.ARCHIVE:
                continue

            if index:
                ui.newline()

            snapshot = Snapshot(repo, create_snapshot_name(), comment=comment)

            ui.info(f"Creating snapshot {snapshot.name} in repository {repo.name}")
            ui.spinner(
                lambda: self.borg.create_snapshot(snapshot, [path], dry_run=dry_run, progress=True),
                message="Creating snapshot",
            )

            ui.info(f"Compacting repository {repo.name}")
            if random.random() < repo.compact_probability:
                ui.spinner(
                    lambda: self.borg.compact(repo, dry_run=dry_run, progress=True),
                    message="Compacting",
                )

            ui.success("Archive completed")
            index += 1
