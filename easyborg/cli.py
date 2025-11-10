from pathlib import Path

import typer

from easyborg.config import load_config
from easyborg.core import Core
from easyborg.cron import Cron
from easyborg.logging_setup import setup_logging

app = typer.Typer(
    help="easyborg - Borg for Dummies",
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_short=True,
    pretty_exceptions_show_locals=False,
)

setup_logging()
config = load_config()
core = Core(config, compact_probability=0.10)


@app.command()
def info():
    """
    Outputs info about the current configuration.
    """
    core.info()


@app.command()
def backup(
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not modify data."),
):
    """
    Create a snapshot of configured folders in each backup repository.
    """
    core.backup(dry_run=dry_run)


@app.command()
def archive(
    folder: Path,
    comment: str = typer.Option(None, "--comment", help="Add comment to the created snapshot."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not modify data."),
):
    """
    Create snapshot of given folder in each archive repository.
    """
    core.archive(folder, dry_run=dry_run, comment=comment)


@app.command()
def restore(
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not modify data."),
):
    """
    Restore snapshot to the current working directory.
    """
    core.restore(dry_run=dry_run)


@app.command()
def extract(
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not modify data."),
):
    """
    Interactively extract one or more files/folders from a snapshot.
    """

    core.extract(dry_run=dry_run)


@app.command()
def enable():
    """
    Enable automatic backups.

    On macOS and Linux this creates a system job that runs `easyborg backup` hourly.
    """
    cron = Cron(command="easyborg backup")
    cron.enable("@hourly")


@app.command()
def disable():
    """
    Disable automatic backups.

    Removes previously created system jobs (e.g. crontab entries on macOS/Linux).
    """
    cron = Cron(command="easyborg backup")
    cron.disable()
