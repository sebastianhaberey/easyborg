from easyborg import ui
from easyborg.borg import Borg
from easyborg.fzf import Fzf
from easyborg.interaction import confirm, select_repo, select_snapshot
from easyborg.model import Config


class DeleteCommand:
    def __init__(self, *, config: Config, borg: Borg, fzf: Fzf) -> None:
        super().__init__()
        self.config = config
        self.borg = borg
        self.fzf = fzf

    def run(self, *, dry_run: bool = False) -> None:
        repo = select_repo(self.fzf, self.config)
        if not repo:
            ui.abort()
            return

        snapshot = select_snapshot(self.borg, self.fzf, repo)
        if not snapshot:
            ui.abort()
            return

        response = confirm(self.fzf, "Delete snapshot? ", danger=True)
        if not response:
            ui.abort()
            return

        ui.newline()

        ui.info(f"Deleting snapshot {snapshot.name} from repository {repo.name}")
        ui.spinner(
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
