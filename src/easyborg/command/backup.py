import random

from easyborg import ui
from easyborg.borg import Borg
from easyborg.model import Config, RepositoryType, Snapshot
from easyborg.util import create_snapshot_name


class BackupCommand:
    def __init__(self, *, config: Config, borg: Borg):
        super().__init__()
        self.config = config
        self.borg = borg

    def run(self, *, dry_run: bool = False, tenacious=False) -> None:
        """
        Create snapshot of all configured folders in each repository configured as 'backup'.
        """

        index = 0
        for repo in self.config.repos.values():
            if repo.type is not RepositoryType.BACKUP:
                continue

            try:
                if index:
                    ui.newline()

                snapshot = Snapshot(repo, create_snapshot_name())

                ui.info(f"Creating snapshot {snapshot.name} in repository {repo.name}")
                ui.spinner(
                    lambda: self.borg.create_snapshot(
                        snapshot,
                        self.config.backup_folders,
                        dry_run=dry_run,
                        progress=True,
                    ),
                )

                ui.info(f"Pruning old snapshots in repository {repo.name}")
                ui.spinner(
                    lambda: self.borg.prune(repo, dry_run=dry_run, progress=True),
                )

                if random.random() < repo.compact_probability:
                    ui.info(f"Compacting repository {repo.name}")
                    ui.spinner(
                        lambda: self.borg.compact(repo, dry_run=dry_run, progress=True),
                    )

                ui.success("Backup completed")
            except Exception as e:
                if tenacious:
                    ui.exception(e)  # don't throw, keep going
                else:
                    raise e
            finally:
                index += 1
