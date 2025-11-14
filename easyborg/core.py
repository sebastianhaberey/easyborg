from __future__ import annotations

import random
from collections.abc import Iterator
from pathlib import Path

from easyborg import ui
from easyborg.borg import Borg
from easyborg.fzf import Fzf, SortOrder
from easyborg.logging_setup import get_current_log_file, get_current_log_level
from easyborg.model import Config, ProgressEvent, Repository, RepositoryType, Snapshot
from easyborg.util import create_snapshot_name, remove_redundant_paths


class Core:
    """
    High-level orchestration layer that coordinates configuration,
    Borg backup operations, and interactive selection via fzf.
    """

    def __init__(self, config: Config, borg: Borg | None = None, fzf: Fzf | None = None, compact_probability=1.0):
        """
        Initialize the controller.
        """

        self.config = config
        self.repos = config.repos
        self.folders = config.folders
        self.borg = borg or Borg()
        self.fzf = fzf or Fzf()
        self.compact_probability = compact_probability

    def info(self) -> None:
        """
        Display configuration details.
        """
        ui.header("Configuration")
        ui.out(f"  - [cyan]Configuration file[/cyan] {self.config.source}", write_log=False)
        ui.out(f"  - [cyan]Log file[/cyan] {get_current_log_file() or 'not configured'}", write_log=False)
        ui.out(f"  - [cyan]Log level[/cyan] {get_current_log_level() or 'not configured'}", write_log=False)
        ui.newline()

        ui.header("Backup Folders")
        if self.folders:
            for folder in self.folders:
                ui.out(f"  - {folder}", write_log=False)
        else:
            ui.out("No backup folders configured.", write_log=False)
        ui.newline()

        ui.header("Repositories")
        if self.repos:
            for repo in self.repos.values():
                ui.out(f"  - {repo.name}: {repo.url} ({repo.type.value})", write_log=False)
        else:
            ui.out("  No repositories configured.", write_log=False)

    def backup(self, dry_run: bool = False) -> None:
        """
        Create snapshot of all configured folders in each repository configured as 'backup'.
        """

        index = 0
        for repo in self.repos.values():
            if repo.type is not RepositoryType.BACKUP:
                continue

            if index:
                ui.newline()

            snapshot = Snapshot(repo, create_snapshot_name())

            ui.out(f"Creating snapshot '{snapshot.name}' in repository '{repo.name}'")
            ui.spinner(
                lambda: self.borg.create_snapshot(snapshot, self.folders, dry_run=dry_run, progress=True),
            )

            ui.out(f"Pruning old snapshots in repository '{repo.name}'")
            ui.spinner(
                lambda: self.borg.prune(repo, dry_run=dry_run, progress=True),
            )

            if random.random() < self.compact_probability:
                ui.out(f"Compacting repository '{repo.name}' (random chance {_get_percent(self.compact_probability)}%)")
                ui.spinner(
                    lambda: self.borg.compact(repo, dry_run=dry_run, progress=True),
                )

            ui.success("Backup complete")
            index += 1

    def archive(self, folder: Path, dry_run: bool = False, comment: str | None = None) -> None:
        """
        Create snapshot of specified folder in each repository configured as 'archive'.
        """

        if not folder.is_dir():
            raise RuntimeError(f"Folder does not exist: {folder}")

        index = 0
        for repo in self.repos.values():
            if repo.type is not RepositoryType.ARCHIVE:
                continue

            if index:
                ui.newline()

            snapshot = Snapshot(repo, create_snapshot_name(), comment=comment)

            ui.out(f"Creating snapshot '{snapshot.name}' in repository '{repo.name}'")
            ui.spinner(
                lambda: self.borg.create_snapshot(snapshot, [folder], dry_run=dry_run, progress=True),
            )

            ui.out(f"Compacting repository '{repo.name}' (random chance {_get_percent(self.compact_probability)}%)")
            if random.random() < self.compact_probability:
                ui.spinner(
                    lambda: self.borg.compact(repo, dry_run=dry_run, progress=True),
                )

            ui.success("Archive complete")
            index += 1

    def restore(self, dry_run: bool = False) -> None:
        """
        Interactively restore entire snapshot.
        """

        repo = self._select_repo()
        if not repo:
            ui.warn("Aborted")
            return

        snapshots: list[Snapshot] | None = None

        def list_snapshots(repo: Repository) -> Iterator[ProgressEvent]:
            nonlocal snapshots
            snapshots = self.borg.list_snapshots(repo)
            return iter([])

        ui.out(f"Listing snapshots in repository '{repo.name}'")
        ui.spinner(
            lambda: list_snapshots(repo),
        )
        snapshot = self._select_snapshot(snapshots)
        if not snapshot:
            ui.warn("Aborted")
            return

        target_dir = Path.cwd()

        ui.out(f"Restoring snapshot '{snapshot.name}' from repository '{repo.name}'")
        ui.progress(
            lambda: self.borg.restore(
                snapshot,
                target_dir,
                dry_run=dry_run,
                progress=True,
            ),
        )
        ui.success("Restore complete")

    def extract(self, dry_run: bool = False) -> None:
        """
        Interactively extract selected files / folders from snapshot.
        """

        repo = self._select_repo()
        if not repo:
            ui.warn("Aborted")
            return

        snapshots: list[Snapshot] | None = None

        def list_snapshots(repo: Repository) -> Iterator[ProgressEvent]:
            nonlocal snapshots
            snapshots = self.borg.list_snapshots(repo)
            return iter([])

        ui.out(f"Listing snapshots in repository '{repo.name}'")
        ui.spinner(
            lambda: list_snapshots(repo),
        )

        snapshot = self._select_snapshot(snapshots)
        if not snapshot:
            ui.warn("Aborted")
            return

        selected_paths = self._select_paths(snapshot)
        if not selected_paths:
            ui.warn("Aborted")
            return

        selected_paths = remove_redundant_paths(selected_paths)
        target_dir = Path.cwd()
        item_count = len(selected_paths)
        item_str = "one item" if item_count == 1 else f"{item_count} items"

        ui.out(f"Extracting {item_str} from snapshot '{snapshot.name}' in repository '{repo.name}'")
        ui.progress(
            lambda: self.borg.restore(
                snapshot,
                target_dir=target_dir,
                folders=selected_paths,
                dry_run=dry_run,
                progress=True,
            ),
        )

        ui.success("Extract complete")

    def _select_repo(self) -> Repository | None:
        repos = self.fzf.select_items(
            self.repos.values(),
            key=lambda r: r.name,
            prompt="Select repository: ",
        )
        return repos[0] if repos else None

    def _select_snapshot(self, snapshots: list[Snapshot]) -> Snapshot | None:
        snapshot = self.fzf.select_items(
            snapshots,
            key=lambda s: f"{s.name} — {s.comment}" if s.comment else s.name,
            prompt="Select snapshot: ",
            sort_order=SortOrder.DESCENDING,
        )
        return snapshot[0] if snapshot else None

    def _select_paths(self, snapshot: Snapshot) -> list[Path]:
        path_strings = self.fzf.select_strings(
            map(str, self.borg.list_contents(snapshot)),
            multi=True,
            prompt="Select items to extract: ",
        )
        return [Path(s) for s in path_strings]


def _get_percent(value: float) -> int:
    value = max(0.0, min(1.0, value))
    return int(round(value * 100))
