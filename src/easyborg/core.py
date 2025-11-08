from __future__ import annotations

from pathlib import Path

from easyborg import ui
from easyborg.borg import Borg
from easyborg.fzf import Fzf
from easyborg.model import Config, RepositoryType, Snapshot
from easyborg.util import create_snapshot_name, find_snapshot_by_name


class Core:
    """
    High-level orchestration layer that coordinates configuration,
    Borg backup operations, and interactive selection via fzf.
    """

    def __init__(self, config: Config, borg: Borg | None = None, fzf: Fzf | None = None):
        """
        Initialize the controller using the given configuration.
        """
        self.config = config
        self.repos = config.repos
        self.folders = config.folders
        self.borg = borg or Borg()
        self.fzf = fzf or Fzf()

    def info(self) -> None:
        """
        Display configuration details in a human-friendly format.
        """
        ui.newline()
        ui.table(title="Configuration", headers=["Path"], rows=[(str(self.config.source),)])
        ui.table(
            title="Backup Folders",
            headers=["Folder"],
            rows=[(str(folder),) for folder in self.folders],
        )
        ui.table(
            title="Repositories",
            headers=["Name", "Type", "Path"],
            rows=[
                (
                    repo.name,
                    repo.type.value,
                    repo.url,
                )
                for repo in self.repos.values()
            ],
        )
        ui.newline()

    def backup(self, dry_run: bool = False) -> None:
        """
        Create a snapshot of all configured folders in each repository configured as type 'backup'.
        :param dry_run:
        """
        for repo in self.repos.values():
            if repo.type is not RepositoryType.BACKUP:
                continue

            if not self.borg.repository_accessible(repo):
                raise RuntimeError(f"Repository not accessible: {repo.name} ({repo.url})")

            snapshot = Snapshot(repo, create_snapshot_name())
            ui.info(f"Creating snapshot {snapshot.name} in {repo.name} ({repo.url})")
            self.borg.create_snapshot(snapshot, self.folders, dry_run=dry_run)

        ui.success("Backup complete")

    def archive(self, folder: Path, dry_run: bool = False) -> None:
        """
        Create a snapshot of the specified folder in each repository configured as type 'archive'.
        :param dry_run:
        """
        if not folder.is_dir():
            raise RuntimeError(f"Folder does not exist: {folder}")

        for repo in self.repos.values():
            if repo.type is not RepositoryType.ARCHIVE:
                continue

            if not self.borg.repository_accessible(repo):
                raise RuntimeError(f"Repository not accessible: {repo.name} ({repo.url})")

            snapshot = Snapshot(repo, create_snapshot_name())
            ui.info(f"Creating snapshot {snapshot.name} in {repo.name} ({repo.url})")
            self.borg.create_snapshot(snapshot, [folder], dry_run=dry_run)

        ui.success("Archive complete")

    def restore(
        self,
        repo_name: str | None = None,
        snapshot_name: str | None = None,
        target_dir: Path | None = None,
        dry_run: bool = False,
    ) -> None:
        """
        Restore a snapshot. If parameters are omitted, prompt interactively via fzf.
        :param dry_run:
        """
        # Select repository
        if repo_name is None:
            repo_name = self.fzf.select_one(
                self.repos.keys(),
                prompt="Select repository: ",
            )
            if repo_name is None:
                ui.warn("Aborted")
                return

        repo = self.repos[repo_name]

        if not self.borg.repository_accessible(repo):
            raise RuntimeError(f"Repository not accessible: {repo.name} ({repo.url})")

        # Select snapshot
        snapshots = self.borg.list_snapshots(repo)

        if snapshot_name is None:
            snapshot_name = self.fzf.select_one(
                (s.name for s in snapshots),
                prompt="Select snapshot: ",
            )
            if snapshot_name is None:
                ui.warn("Aborted")
                return

        snapshot = find_snapshot_by_name(snapshot_name, snapshots)

        # Default target directory is current working directory
        if target_dir is None:
            target_dir = Path.cwd()

        ui.info(f"Restoring {snapshot.name} from {repo.name} ({repo.url})")
        self.borg.restore(snapshot, target_dir, dry_run=dry_run)
        ui.success("Restore complete")
