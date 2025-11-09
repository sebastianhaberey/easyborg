from __future__ import annotations

import random
from pathlib import Path

from easyborg import ui
from easyborg.borg import Borg
from easyborg.fzf import Fzf
from easyborg.model import Config, RepositoryType, Snapshot
from easyborg.util import create_snapshot_name


class Core:
    """
    High-level orchestration layer that coordinates configuration,
    Borg backup operations, and interactive selection via fzf.
    """

    def __init__(self, config: Config, borg: Borg | None = None, fzf: Fzf | None = None):
        """
        Initialize the controller.
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
            rows=[(repo.name, repo.type.value, repo.url) for repo in self.repos.values()],
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

            ui.info(f"Pruning old snapshots in {repo.name} ({repo.url})")
            self.borg.prune(repo, dry_run=dry_run)

            if random.random() < 0.10:
                ui.info(f"(Random check) Compacting repository {repo.name} ({repo.url})")
                self.borg.compact(repo, dry_run=dry_run)

        ui.success("Backup complete")

    def archive(self, folder: Path, dry_run: bool = False, comment: str | None = None) -> None:
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

            snapshot = Snapshot(repo, create_snapshot_name(), comment=comment)
            ui.info(f"Creating snapshot {snapshot.name} in {repo.name} ({repo.url})")
            self.borg.create_snapshot(snapshot, [folder], dry_run=dry_run)

            ui.info(f"Pruning old snapshots in {repo.name} ({repo.url})")
            self.borg.prune(repo, dry_run=dry_run)

            if random.random() < 0.10:
                ui.info(f"(Random check) Compacting repository {repo.name} ({repo.url})")
                self.borg.compact(repo, dry_run=dry_run)

        ui.success("Archive complete")

    def restore(self, dry_run: bool = False) -> None:
        """
        Interactively restore entire snapshot.
        """

        # 1) Select repository
        selected = self.fzf.select_item(
            self.repos.values(),
            key=lambda r: r.name,
            prompt="Select repository: ",
            multi=False,
        )
        if not selected:
            ui.warn("Aborted")
            return
        repo = selected[0]

        if not self.borg.repository_accessible(repo):
            raise RuntimeError(f"Repository not accessible: {repo.name} ({repo.url})")

        # 2) Select snapshot
        snapshots = self.borg.list_snapshots(repo)
        snapshots.sort(key=lambda s: s.name, reverse=True)

        selected = self.fzf.select_item(
            snapshots,
            key=lambda s: f"{s.name} — {s.comment}" if s.comment else s.name,
            prompt="Select snapshot: ",
            multi=False,
        )
        if not selected:
            ui.warn("Aborted")
            return
        snapshot = selected[0]

        target_dir = Path.cwd()

        ui.info(f"Restoring {snapshot.name} from {repo.name} ({repo.url})")
        self.borg.restore(snapshot, target_dir, dry_run=dry_run)
        ui.success("Restore complete")

    def extract(self, dry_run: bool = False) -> None:
        """
        Interactively extract selected files / folders from snapshot.
        """

        # 1) Select repository
        selected = self.fzf.select_item(
            self.repos.values(),
            key=lambda r: r.name,
            prompt="Select repository: ",
            multi=False,
        )
        if not selected:
            ui.warn("Aborted")
            return
        repo = selected[0]

        # 2) Select snapshot
        snapshots = self.borg.list_snapshots(repo)
        snapshots.sort(key=lambda s: s.name, reverse=True)

        selected = self.fzf.select_item(
            snapshots,
            key=lambda s: f"{s.name} — {s.comment}" if s.comment else s.name,
            prompt="Select snapshot: ",
            multi=False,
        )
        if not selected:
            ui.warn("Aborted")
            return
        snapshot = selected[0]

        # 3) Select paths
        selected_paths_str = self.fzf.select(
            map(str, self.borg.list_contents(snapshot)),
            prompt="Select items to extract: ",
            multi=True,
        )

        if not selected_paths_str:
            ui.warn("Aborted")
            return

        selected_paths = [Path(p) for p in selected_paths_str]
        target_dir = Path.cwd()

        if not self.borg.repository_accessible(repo):
            raise RuntimeError(f"Repository does not exist or is not accessible: {repo.name} ({repo.url})")

        ui.info(f"Extracting {len(selected_paths)} item(s) from repository {repo.name}, snapshot {snapshot.name}")
        self.borg.restore(snapshot, target_dir=target_dir, folders=selected_paths, dry_run=dry_run)
        ui.success("Extract complete")
