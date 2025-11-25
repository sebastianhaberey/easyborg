from pathlib import Path

from easyborg import ui
from easyborg.borg import Borg
from easyborg.fzf import Fzf
from easyborg.interaction import select_items, select_repo, select_snapshot
from easyborg.model import Config


class ExtractCommand:
    def __init__(self, *, config: Config, borg: Borg, fzf: Fzf) -> None:
        super().__init__()
        self.config = config
        self.borg = borg
        self.fzf = fzf

    def run(self, *, dry_run: bool = False) -> None:
        """
        Interactively extract selected items from snapshot.
        """

        repo = select_repo(self.fzf, self.config)
        if not repo:
            ui.abort()
            return

        snapshot = select_snapshot(self.borg, self.fzf, repo)
        if not snapshot:
            ui.abort()
            return

        selected_paths = select_items(self.borg, self.fzf, snapshot)
        if not selected_paths:
            ui.abort()
            return

        ui.newline()

        target_dir = Path.cwd()

        ui.info(f"Extracting {len(selected_paths)} item(s) from snapshot {snapshot.name} in repository {repo.name}")
        ui.progress(
            lambda: self.borg.restore(
                snapshot,
                target_dir=target_dir,
                paths=selected_paths,
                dry_run=dry_run,
                progress=True,
            ),
            message="Extracting",
        )

        ui.success("Extract completed")
