from pathlib import Path

import click
from easyborg.config import load_config
from easyborg.core import Core
from easyborg.cron import Cron
from easyborg.logging_setup import setup_logging

# Initialize once, like before
setup_logging()
config = load_config()
core = Core(config, compact_probability=0.10)


@click.group(help="easyborg – Borg for Dummies")
@click.version_option(package_name="easyborg")
def cli():
    """Main easyborg command group."""
    pass


@cli.command()
def info():
    """Outputs info about the current configuration."""
    core.info()


@cli.command()
@click.option("--dry-run", is_flag=True, help="Do not modify data.")
def backup(dry_run: bool):
    """Create a snapshot of configured folders in each backup repository."""
    core.backup(dry_run=dry_run)


@cli.command()
@click.argument("folder", type=click.Path(path_type=Path, exists=True))
@click.option("--comment", help="Add comment to the created snapshot.")
@click.option("--dry-run", is_flag=True, help="Do not modify data.")
def archive(folder: Path, comment: str | None, dry_run: bool):
    """Create a snapshot of the given folder in each archive repository."""
    core.archive(folder, dry_run=dry_run, comment=comment)


@cli.command()
@click.option("--dry-run", is_flag=True, help="Do not modify data.")
def restore(dry_run: bool):
    """Restore snapshot to the current working directory."""
    core.restore(dry_run=dry_run)


@cli.command()
@click.option("--dry-run", is_flag=True, help="Do not modify data.")
def extract(dry_run: bool):
    """Interactively extract one or more files/folders from a snapshot."""
    core.extract(dry_run=dry_run)


@cli.command()
def enable():
    """Enable automatic backups (runs 'easyborg backup' hourly)."""
    cron = Cron(command="easyborg backup")
    cron.enable("@hourly")


@cli.command()
def disable():
    """Disable automatic backups."""
    cron = Cron(command="easyborg backup")
    cron.disable()
