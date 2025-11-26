from pathlib import Path

from easyborg import ui
from easyborg.borg import Borg
from easyborg.fzf import Fzf
from easyborg.interaction import select_repo, select_snapshot
from easyborg.model import Config


class RestoreCommand:
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

        ui.newline()

        target_dir = Path.cwd()

        ui.info(f"Restoring snapshot {snapshot.name} from repository {repo.name}")
        ui.progress(
            lambda: self.borg.restore(
                snapshot,
                target_dir,
                dry_run=dry_run,
                progress=True,
            ),
            message="Restoring snapshot",
        )

        ui.success("Restore completed")
