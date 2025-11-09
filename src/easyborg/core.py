from __future__ import annotations

import random
from pathlib import Path

from easyborg import ui
from easyborg.borg import Borg
from easyborg.fzf import Fzf, SortOrder
from easyborg.model import Config, Repository, RepositoryType, Snapshot
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

        repo = self._select_repo()
        if not repo:
            ui.warn("Aborted")
            return

        snapshot = self._select_snapshot(repo)
        if not snapshot:
            ui.warn("Aborted")
            return

        target_dir = Path.cwd()

        ui.info(f"Restoring snapshot {snapshot.name} from repository {repo.name} ({repo.url})")
        self.borg.restore(snapshot, target_dir, dry_run=dry_run)
        ui.success("Restore complete")

    def extract(self, dry_run: bool = False) -> None:
        """
        Interactively extract selected files / folders from snapshot.
        """

        repo = self._select_repo()
        if not repo:
            ui.warn("Aborted")
            return

        snapshot = self._select_snapshot(repo)
        if not snapshot:
            ui.warn("Aborted")
            return

        selected_paths = self._select_paths(snapshot)
        if not selected_paths:
            ui.warn("Aborted")
            return

        target_dir = Path.cwd()

        ui.info(f"Extracting {len(selected_paths)} item(s) from snapshot {snapshot.name}, repository {repo.name}")
        self.borg.restore(snapshot, target_dir=target_dir, folders=selected_paths, dry_run=dry_run)
        ui.success("Extract complete")

    def _select_repo(self) -> Repository:
        repo = self.fzf.select_one_item(
            self.repos.values(),
            key=lambda r: r.name,
            prompt="Select repository: ",
        )
        if repo is not None and not self.borg.repository_accessible(repo):
            raise RuntimeError(f"Repository not accessible: {repo.name} ({repo.url})")
        return repo

    def _select_snapshot(self, repo) -> Snapshot:
        snapshot = self.fzf.select_one_item(
            self.borg.list_snapshots(repo),
            key=lambda s: f"{s.name} — {s.comment}" if s.comment else s.name,
            prompt="Select snapshot: ",
            sortOrder=SortOrder.DESCENDING,
        )
        return snapshot

    def _select_paths(self, snapshot: Snapshot) -> list[Path]:
        selected_paths = [
            Path(p)
            for p in self.fzf.select_multiple_strings(
                map(str, self.borg.list_contents(snapshot)),
                prompt="Select items to extract: ",
            )
        ]
        return selected_paths
