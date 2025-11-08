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
        Display configuration details.
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
        Create snapshot of all configured folders in each repository configured as 'backup'.
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
        Create snapshot of specified folder in each repository configured as 'archive'.
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

    def restore(self, dry_run: bool = False) -> None:
        """
        Interactively restore entire snapshot.
        """

        # 1) Select repository
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

        # 2) Select snapshot
        snapshots = self.borg.list_snapshots(repo)

        snapshot_name = self.fzf.select_one(
            (s.name for s in snapshots),
            prompt="Select snapshot: ",
        )
        if snapshot_name is None:
            ui.warn("Aborted")
            return

        snapshot = find_snapshot_by_name(snapshot_name, snapshots)

        # 3) Target directory is current working directory
        target_dir = Path.cwd()

        ui.info(f"Restoring {snapshot.name} from {repo.name} ({repo.url})")
        self.borg.restore(snapshot, target_dir, dry_run=dry_run)
        ui.success("Restore complete")

    def extract(self, dry_run: bool = False) -> None:
        """
        Interactively extract selected files / folders from snapshot.
        """

        # 1) Select repository
        repo_name = self.fzf.select_one(
            (name for name in self.repos.keys()),
            prompt="Select repository: ",
        )
        if repo_name is None:
            ui.warn("Aborted")
            return

        repo = self.repos[repo_name]

        # 2) Select snapshot
        snapshots = self.borg.list_snapshots(repo)

        snapshot_name = self.fzf.select_one(
            (s.name for s in snapshots),
            prompt="Select snapshot: ",
        )
        if snapshot_name is None:
            ui.warn("Aborted")
            return

        snapshot = find_snapshot_by_name(snapshot_name, snapshots)

        # 3) Select files/folders
        selected_items = self.fzf.select_many(
            (str(p) for p in self.borg.list_contents(snapshot)),
            prompt="Select items to extract: ",
        )

        if not selected_items:
            ui.warn("Aborted")
            return

        selected_paths = [Path(s) for s in selected_items]

        # 4) Determine target dir
        target_dir = Path.cwd()

        if not self.borg.repository_accessible(repo):
            raise RuntimeError(f"Repository does not exist or is not accessible: {repo.name} ({repo.url})")

        # 5) Perform extraction
        ui.info(f"Extracting {len(selected_paths)} item(s) from snapshot {snapshot.name} in {repo.name} ({repo.url})")
        self.borg.restore(snapshot, target_dir=target_dir, folders=selected_paths, dry_run=dry_run)
        ui.success("Extract complete")
