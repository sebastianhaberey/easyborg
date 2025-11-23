from collections.abc import Iterator

from easyborg import ui
from easyborg.borg import Borg
from easyborg.fzf import Fzf
from easyborg.interaction import select_repo, select_snapshot
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

        ui.info("Select snapshot")
        ui.spinner(
            lambda: list_snapshots(repo),
            message="Listing snapshots",
        )
        snapshot = select_snapshot(self.fzf, snapshots)
        if not snapshot:
            ui.warn("Aborted")
            return
        ui.selected(snapshot.full_name())

        ui.info("Delete snapshot?")
        confirm = self.fzf.confirm()
        if not confirm:
            ui.warn("Aborted")
            return
        ui.selected("YES")
        ui.newline()

        ui.info(f"Deleting snapshot {snapshot.name} from repository {repo.name}")
        ui.progress(
            lambda: self.borg.delete(
                snapshot,
                dry_run=dry_run,
                progress=True,
            ),
            message="Deleting",
        )

        ui.info(f"Compacting repository {repo.name}")
        ui.spinner(
            lambda: self.borg.compact(repo, dry_run=dry_run, progress=True),
            message="Compacting",
        )

        ui.success("Delete completed")
