from pathlib import Path

import typer

from easyborg.config import Config
from easyborg.core import Core

app = typer.Typer(
    help="easyborg - Borg for Dummies",
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_short=True,  # TODO SH show stack trace in debug mode only
    pretty_exceptions_show_locals=False,
)

config = Config.load()
core = Core(config)


@app.command()
def info():
    """
    Outputs info about the current configuration.
    """

    core.info()
    return


@app.command()
def backup():
    """
    Create a snapshot of configured folders in each backup repository
    """

    core.backup()
    return


@app.command()
def archive(
    folder: Path,
):
    """
    Create snapshot of given folder in each archive repository
    """

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

    core.restore(repo, snapshot)
