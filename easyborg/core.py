from __future__ import annotations

import random
from collections.abc import Iterator
from pathlib import Path

from easyborg import ui
from easyborg.borg import Borg
from easyborg.context import Context
from easyborg.fzf import Fzf, SortOrder
from easyborg.model import Config, ProgressEvent, Repository, RepositoryType, Snapshot
from easyborg.ui import link_path, render_dict
from easyborg.util import create_snapshot_name, remove_redundant_paths


class Core:
    """
    High-level orchestration layer that coordinates configuration,
    Borg backup operations, and interactive selection via fzf.
    """

    def __init__(self, config: Config, borg: Borg, fzf: Fzf):
        """
        Initialize the controller.
        """
        self.config = config
        self.repos = config.repos
        self.backup_folders = config.backup_folders
        self.borg = borg
        self.fzf = fzf

    def info(self, context: Context) -> None:
        """
        Display configuration details.
        """
        rows = [
            ("Configuration directory", link_path(context.config_dir)),
            ("Configuration file", link_path(context.config_file)),
            ("Log directory", link_path(context.log_dir) if context.log_dir else "not configured"),
            ("Log file", link_path(context.log_file) if context.log_file else "not configured"),
            ("Easyborg executable path", context.easyborg_executable),
            ("Borg executable path", context.borg_executable),
            ("fzf executable path", context.fzf_executable),
        ]
        if context.expert:
            rows.extend(
                [
                    ("Expert mode", context.expert),
                    ("Debug mode", context.debug),
                    ("Profile", context.profile),
                ]
            )
        ui.header("Configuration")
        ui.table(rows, column_colors=(None, "bold cyan"))

        if context.expert:
            ui.header("Environment")
            rows = [(key, value) for key, value in self.config.env.items()]
            ui.table(rows, headers=("Variable", "Value"), column_colors=(None, "bold cyan"))

        ui.header("Backup Folders")
        if self.backup_folders:
            rows = [(link_path(folder),) for folder in self.backup_folders]
            ui.table(rows, column_colors=("bold cyan",))
        else:
            ui.newline()
            ui.out("(no backup folders configured)", indent=1)
            ui.newline()

        ui.header("Repositories")
        if self.repos:
            rows = [(repo.name, repo.url, repo.type.value) for repo in self.repos.values()]
            ui.table(
                rows,
                column_colors=(None, "bold cyan", "bold magenta"),
                headers=("Name", "URL", "Type"),
            )
        else:
            ui.newline()
            ui.out("(no repositories configured)", indent=1)
            ui.newline()

        if self.repos and context.expert:
            ui.header("Repository Environments")
            rows = [(repo.name, render_dict(repo.env, separator="\n")) for repo in self.repos.values()]
            ui.table(
                rows,
                headers=("Repository", "Environment"),
                column_colors=(None, None),
            )

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

            ui.info(f"Creating snapshot '{snapshot.name}' in repository '{repo.name}'")
            ui.spinner(
                lambda: self.borg.create_snapshot(snapshot, self.backup_folders, dry_run=dry_run, progress=True),
            )

            ui.info(f"Pruning old snapshots in repository '{repo.name}'")
            ui.spinner(
                lambda: self.borg.prune(repo, dry_run=dry_run, progress=True),
            )

            if random.random() < repo.compact_probability:
                ui.info(f"Compacting repository '{repo.name}'")
                ui.spinner(
                    lambda: self.borg.compact(repo, dry_run=dry_run, progress=True),
                )

            ui.success("Backup completed")
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

            ui.info(f"Creating snapshot '{snapshot.name}' in repository '{repo.name}'")
            ui.spinner(
                lambda: self.borg.create_snapshot(snapshot, [folder], dry_run=dry_run, progress=True),
            )

            ui.info(f"Compacting repository '{repo.name}'")
            if random.random() < repo.compact_probability:
                ui.spinner(
                    lambda: self.borg.compact(repo, dry_run=dry_run, progress=True),
                )

            ui.success("Archive completed")
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

        ui.info(f"Listing snapshots in repository '{repo.name}'")
        ui.spinner(
            lambda: list_snapshots(repo),
        )
        snapshot = self._select_snapshot(snapshots)
        if not snapshot:
            ui.warn("Aborted")
            return

        target_dir = Path.cwd()

        ui.info(f"Restoring snapshot '{snapshot.name}' from repository '{repo.name}'")
        ui.progress(
            lambda: self.borg.restore(
                snapshot,
                target_dir,
                dry_run=dry_run,
                progress=True,
            ),
        )
        ui.success("Restore completed")

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

        ui.info(f"Listing snapshots in repository '{repo.name}'")
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

        ui.info(f"Extracting {item_str} from snapshot '{snapshot.name}' in repository '{repo.name}'")
        ui.progress(
            lambda: self.borg.restore(
                snapshot,
                target_dir=target_dir,
                folders=selected_paths,
                dry_run=dry_run,
                progress=True,
            ),
        )

        ui.success("Extract completed")

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

    def delete(self, dry_run: bool = False) -> None:
        """
        Interactively delete entire snapshot.
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

        ui.info(f"Listing snapshots in repository '{repo.name}'")
        ui.spinner(
            lambda: list_snapshots(repo),
        )
        snapshot = self._select_snapshot(snapshots)
        if not snapshot:
            ui.warn("Aborted")
            return

        response = self.fzf.confirm(f"Delete snaphshot '{snapshot.name}' from repository '{repo.name}': ")
        if not response:
            ui.warn("Aborted")
            return

        ui.info(f"Deleting snapshot '{snapshot.name}' from repository '{repo.name}'")
        ui.progress(
            lambda: self.borg.delete(
                snapshot,
                dry_run=dry_run,
                progress=True,
            ),
        )

        ui.info(f"Compacting repository '{repo.name}'")
        ui.spinner(
            lambda: self.borg.compact(repo, dry_run=dry_run, progress=True),
        )

        ui.success("Delete completed")


def _get_percent(value: float) -> int:
    value = max(0.0, min(1.0, value))
    return int(round(value * 100))
