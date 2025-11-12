from pathlib import Path
from typing import Any

import cloup
from click import version_option
from cloup import Context, HelpFormatter, HelpTheme, Style, argument, command, group, option
from easyborg import ui
from easyborg.config import load_config
from easyborg.core import Core
from easyborg.cron import Cron
from easyborg.logging_setup import setup_logging
from easyborg.model import Config

context_settings: dict[str, Any] | None = None
config: Config | None = None
core: Core | None = None


def main() -> None:
    try:
        ui.newline()

        global config, core, context_settings

        context_settings = Context.settings(
            # parameters of Command:
            formatter_settings=HelpFormatter.settings(
                theme=HelpTheme(
                    invoked_command=Style(fg="magenta", bold=True),
                    heading=Style(fg="yellow", bold=True),
                    col1=Style(fg="cyan", bold=True),
                ),
            ),
        )

        setup_logging()
        config = load_config()
        core = Core(config, compact_probability=0.10)

        cli()

    except Exception as e:
        ui.error(f"{e}")
    finally:
        ui.newline()


@group(help="easyborg – Borg for Dummies", context_settings=context_settings)
@version_option(package_name="easyborg")
def cli():
    pass


@command()
@option("--dry-run", is_flag=True, help="Do not modify data.")
def backup(dry_run: bool):
    """Create snapshot of configured folders in backup repositories"""
    core.backup(dry_run=dry_run)


@command()
@argument("folder", type=cloup.Path(path_type=Path, exists=True), help="Folder to backup.")
@option("--comment", help="Add comment to the created snapshot.")
@option("--dry-run", is_flag=True, help="Do not modify data.")
def archive(folder: Path, comment: str | None, dry_run: bool):
    """Create snapshot of specified folder in archive repositories"""
    core.archive(folder, dry_run=dry_run, comment=comment)


@command()
@option("--dry-run", is_flag=True, help="Do not modify data.")
def restore(dry_run: bool):
    """Restore snapshot to current working directory"""
    core.restore(dry_run=dry_run)


@command()
@cloup.option("--dry-run", is_flag=True, help="Do not modify data.")
def extract(dry_run: bool):
    """Interactively extract files / folders from snapshot"""
    core.extract(dry_run=dry_run)


@command()
def info():
    """Output info about the current configuration"""
    core.info()


@command()
def enable():
    """Enable automatic backups (runs 'easyborg backup' hourly)"""
    cron = Cron(command="easyborg backup")
    cron.enable("@hourly")


@command()
def disable():
    """Disable automatic backups"""
    cron = Cron(command="easyborg backup")
    cron.disable()


cli.section(
    "Main Commands",
    backup,
    archive,
    restore,
    extract,
)

cli.section(
    "Utility Commands",
    info,
    enable,
    disable,
)
