from __future__ import annotations

from pathlib import Path

from easyborg import ui
from easyborg.borg import Borg
from easyborg.config import Config, Repo, RepoType
from easyborg.fzf import Fzf
from easyborg.util import create_snapshot_name


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
            headers=["Name", "Type", "Path", "Status"],
            rows=[
                (
                    repo.name,
                    repo.type.value,
                    repo.path,
                    self._get_repo_status(repo),
                )
                for repo in self.repos.values()
            ],
        )
        ui.newline()

    def backup(self) -> None:
        """
        Create one snapshot in each repository configured as type 'backup',
        containing all configured folders.
        """
        for repo in self.repos.values():
            if not self.borg.repository_accessible(repo.path):
                raise RuntimeError(f"Repository does not exist or is not accessible: {repo.name} ({repo.path})")
            if repo.type is RepoType.BACKUP:
                continue
            snapshot_name = create_snapshot_name()
            ui.info(f"Creating snapshot {snapshot_name} in repository {repo.name} ({repo.path})")
            self.borg.create_snapshot(repo.path, snapshot_name, self.folders)

        ui.success("Backup complete")

    def archive(self, folder: Path) -> None:
        """
        Create a snapshot of one folder in all repositories configured as type 'archive'.
        """
        if not folder.is_dir():
            raise RuntimeError(f"Folder does not exist: {folder}")

        for repo in self.repos.values():
            if not self.borg.repository_accessible(repo.path):
                raise RuntimeError(f"Repository does not exist or is not accessible: {repo.name} ({repo.path})")
            if repo.type is not RepoType.ARCHIVE:
                continue
            snapshot_name = create_snapshot_name()
            ui.info(f"Creating snapshot {snapshot_name} in repository {repo.name} ({repo.path})")
            self.borg.create_snapshot(repo.path, snapshot_name, [folder])

        ui.success("Archive complete")

    def restore(
        self,
        repo_name: str | None = None,
        snapshot: str | None = None,
        target_dir: Path | None = None,
    ) -> None:
        """
        Interactively restore items from a snapshot.
        If parameters are omitted, the user is prompted via fzf.
        """
        # Select repository
        if repo_name is None:
            repo_name = self.fzf.select_one(
                (name for name in self.repos.keys()),
                prompt="Select repository: ",
            )
            if repo_name is None:
                ui.warn("Aborted")
                return

        repo = self.repos[repo_name]

        # Select snapshot
        if snapshot is None:
            snapshot = self.fzf.select_one(
                self.borg.list_snapshots(repo.path),
                prompt="Select snapshot: ",
            )
            if snapshot is None:
                ui.warn("Aborted")
                return

        # Default target directory is current working directory
        if target_dir is None:
            target_dir = Path.cwd()

        if not self.borg.repository_accessible(repo.path):
            raise RuntimeError(f"Repository does not exist or is not accessible: {repo.name} ({repo.path})")

        if not self.borg.snapshot_exists(repo.path, snapshot):
            raise RuntimeError(f"Snapshot does not exist in repo {repo.name} ({repo.path}): {snapshot}")

        # Restore
        ui.info(f"Restoring snapshot {snapshot} from repository {repo.name} ({repo.path}) ")
        self.borg.restore(repository=repo.path, snapshot=snapshot, target_dir=target_dir)
        ui.success("Restore complete")

    def _get_repo_status(self, repo: Repo) -> str:
        return "OK" if self.borg.repository_accessible(repo.path) else "MISSING"
