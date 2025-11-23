from collections.abc import Iterator
from pathlib import Path

from easyborg import ui
from easyborg.borg import Borg
from easyborg.fzf import Fzf, SortOrder
from easyborg.model import Config, ProgressEvent, Repository, Snapshot


class DeleteCommand:
    def __init__(self, *, config: Config, borg: Borg, fzf: Fzf) -> None:
        super().__init__()
        self.config = config
        self.borg = borg
        self.fzf = fzf

    def run(self, *, dry_run: bool = False) -> None:
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

        ui.info(f"Listing snapshots in repository {repo.name}")
        ui.spinner(
            lambda: list_snapshots(repo),
        )
        snapshot = self._select_snapshot(snapshots, repo.name)
        if not snapshot:
            ui.warn("Aborted")
            return

        response = self.fzf.confirm(f"Delete snaphshot {snapshot.name} from repository {repo.name}: ")
        if not response:
            ui.warn("Aborted")
            return

        ui.info(f"Deleting snapshot {snapshot.name} from repository {repo.name}")
        ui.progress(
            lambda: self.borg.delete(
                snapshot,
                dry_run=dry_run,
                progress=True,
            ),
        )

        ui.info(f"Compacting repository {repo.name}")
        ui.spinner(
            lambda: self.borg.compact(repo, dry_run=dry_run, progress=True),
        )

        ui.success("Delete completed")

    def _select_repo(self) -> Repository | None:
        repos = self.fzf.select_items(
            self.config.repos.values(),
            key=lambda r: r.name,
            prompt="Select repository: ",
        )
        return repos[0] if repos else None

    def _select_snapshot(self, snapshots: list[Snapshot], repo_name: str) -> Snapshot | None:
        snapshot = self.fzf.select_items(
            snapshots,
            key=lambda s: f"{s.name} — {s.comment}" if s.comment else s.name,
            prompt=f"Select snapshot from {repo_name}: ",
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
