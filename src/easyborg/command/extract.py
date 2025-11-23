from collections.abc import Iterator
from pathlib import Path

from easyborg import ui
from easyborg.borg import Borg
from easyborg.fzf import Fzf
from easyborg.interaction import select_paths, select_repo, select_snapshot
from easyborg.model import Config, ProgressEvent, Repository, Snapshot
from easyborg.util import remove_redundant_paths


class ExtractCommand:
    def __init__(self, *, config: Config, borg: Borg, fzf: Fzf) -> None:
        super().__init__()
        self.config = config
        self.borg = borg
        self.fzf = fzf

    def run(self, *, dry_run: bool = False) -> None:
        """
        Interactively extract selected files / folders from snapshot.
        """

        ui.info("Select repository")
        repo = select_repo(self.fzf, self.config)
        if not repo:
            ui.warn("Aborted")
            return
        ui.selected(repo.name)

        snapshots: list[Snapshot] | None = None

        def list_snapshots(repo: Repository) -> Iterator[ProgressEvent]:
            nonlocal snapshots
            snapshots = self.borg.list_snapshots(repo)
            return iter([])

        ui.spinner(
            lambda: list_snapshots(repo),
            message="Listing snapshots",
        )

        ui.info("Select snapshot")
        snapshot = select_snapshot(self.fzf, snapshots)
        if not snapshot:
            ui.warn("Aborted")
            return
        ui.selected(snapshot.full_name())

        ui.info("Select items")
        selected_paths = select_paths(self.borg, self.fzf, snapshot)
        if not selected_paths:
            ui.warn("Aborted")
            return
        selected_paths = remove_redundant_paths(selected_paths)
        item_count = len(selected_paths)
        ui.selected(item_count)
        ui.newline()

        target_dir = Path.cwd()

        ui.info(f"Extracting {item_count} item(s) from snapshot {snapshot.name} in repository {repo.name}")
        ui.progress(
            lambda: self.borg.restore(
                snapshot,
                target_dir=target_dir,
                folders=selected_paths,
                dry_run=dry_run,
                progress=True,
            ),
            message="Extracting",
        )

        ui.success("Extract completed")
