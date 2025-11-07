from pathlib import Path

import typer

from easyborg import ui
from easyborg.config import Config
from easyborg.core import Core

app = typer.Typer(help="easyborg - Borg for Dummies", add_completion=False, no_args_is_help=True)

config = Config.load()
core = Core(config)

@app.command()
def backup():
    """
    Create a snapshot of configured folders in each backup repository
    """

    ui.info("Backup")
    core.backup()
    return


@app.command()
def archive(
    folder: Path,
):
    """
    Create snapshot of given folder in each archive repository
    """

    ui.info(f"Archive: folder {folder}")
    core.archive(folder)
    return

@app.command()
def restore(
    repo: str | None = typer.Argument(None),
    snapshot: str | None = typer.Argument(None),
):
    """
    Restore snapshot to the current working directory
    """

    ui.info(f"Restore: repository {repo}, snapshot {snapshot}")
    core.restore(repo, snapshot)
