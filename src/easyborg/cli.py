import logging
import os
from pathlib import Path

import cloup
from click import Choice, help_option, pass_obj, version_option
from cloup import HelpFormatter, HelpTheme, Section, Style, argument, group, option, pass_context

import easyborg
from easyborg import config, log_utils, ui
from easyborg.borg import Borg
from easyborg.command.archive import ArchiveCommand
from easyborg.command.backup import BackupCommand
from easyborg.command.delete import DeleteCommand
from easyborg.command.extract import ExtractCommand
from easyborg.command.info import InfoCommand
from easyborg.command.open import OpenCommand
from easyborg.command.replace import ReplaceCommand
from easyborg.command.restore import RestoreCommand
from easyborg.cron import Cron
from easyborg.fzf import Fzf
from easyborg.model import Context

logger = logging.getLogger(__name__)

CONTEXT_SETTINGS = cloup.Context.settings(
    formatter_settings=HelpFormatter.settings(
        theme=HelpTheme(
            invoked_command=Style(fg="magenta", bold=True),
            heading=Style(fg="yellow", bold=True),
            col1=Style(fg="cyan", bold=True),
        ),
        width=None,
        max_width=100,  # default is too low (80), but too high will yield really long help text lines
    ),
)

SECTION_MAIN = Section("Main commands")
SECTION_UTILITY = Section("Utility commands")

# TODO SH eliminate this constant and remove protected method access
# noinspection PyProtectedMember
EXPERT_MODE: bool = easyborg.context._is_expert_mode()

# TODO SH find a better way to pass debug flag to exception handling
DEBUG_MODE: bool = False


@group(help="Easyborg – Borg for Dummies", context_settings=CONTEXT_SETTINGS)
@version_option(prog_name="Easyborg", help="Show version information", message="%(prog)s version %(version)s")
@help_option(help="Show this page and exit")
@option(
    "--light-mode",
    envvar="EASYBORG_LIGHT_MODE",
    is_flag=True,
    help="Make colors light-friendly",
)
@option(
    "--profile",
    envvar="EASYBORG_PROFILE",
    type=str,
    help="Select configuration profile",
    default="default",
)
@option(
    "--debug",
    envvar="EASYBORG_DEBUG",
    is_flag=True,
    hidden=not EXPERT_MODE,
    help="Enable debug mode (expert)",
)
@option(
    "--headless",
    is_flag=True,
    hidden=not EXPERT_MODE,
    help="Activate headless mode (e.g. for scheduled runs) (expert)",
)
@option(
    "--borg-executable",
    type=cloup.Path(path_type=Path, exists=True, executable=True, file_okay=True, dir_okay=False),
    hidden=not EXPERT_MODE,
    help="Set BorgBackup executable (expert)",
)
@option(
    "--fzf-executable",
    type=cloup.Path(path_type=Path, exists=True, executable=True, file_okay=True, dir_okay=False),
    hidden=not EXPERT_MODE,
    help="Set BorgBackup executable (expert)",
)
@pass_context
def cli(
    ctx: cloup.Context,
    profile: str,
    debug: bool,
    headless: bool,
    borg_executable: Path | None,
    fzf_executable: Path | None,
    light_mode: bool,
) -> None:
    # first, set DEBUG_MODE flag to enable stacktraces
    global DEBUG_MODE
    DEBUG_MODE = debug

    # next, initialize logging as soon as possible to prevent unwanted output
    log_dir = log_utils.get_log_dir(profile)
    log_file = log_utils.get_log_file(log_dir)

    if headless and ctx.invoked_subcommand in ["backup", "archive"]:
        # TODO SH currently headless only makes sense with non-interactive commands;
        #   find a way to have the option bound to the actual commands
        log_utils.enable_file_logging(log_file, debug)
        ui.disable()
        logger.info("--------------------------------------------------------------------------------")
    else:
        log_utils.disable_logging()

    ctx.ensure_object(dict)

    easyborg_executable = ctx.obj.pop("easyborg_executable", None)  # move info from Click context to Easyborg context

    context = easyborg.context.create(
        profile=profile,
        log_dir=log_dir,
        log_file=log_file,
        debug=debug,
        headless=headless,
        easyborg_executable=easyborg_executable,
        borg_executable=borg_executable,
        fzf_executable=fzf_executable,
    )
    ctx.obj["context"] = context

    configuration = config.load(context.config_file)
    os.environ.update(configuration.env)
    ctx.obj["config"] = configuration

    borg = Borg(executable=context.borg_executable)
    ctx.obj["borg"] = borg

    fzf = Fzf(executable=context.fzf_executable, light_mode=light_mode)
    ctx.obj["fzf"] = fzf


@cli.command(section=SECTION_MAIN)
@option("--dry-run", is_flag=True, help="Do not modify data")
@option(
    "--tenacious",
    is_flag=True,
    hidden=not EXPERT_MODE,
    help="If snapshot creation fails, log error and continue with next repository (expert)",
)
@help_option(help="Show this message and exit")
@pass_obj
def backup(obj, dry_run: bool, tenacious: bool):
    """Create snapshot of configured folders in backup repositories"""
    command = BackupCommand(config=obj["config"], borg=obj["borg"])
    command.run(dry_run=dry_run, tenacious=tenacious)


@cli.command(section=SECTION_MAIN)
@argument("folder", type=cloup.Path(path_type=Path, exists=True), help="Folder to backup")
@option("--comment", help="Add comment to the created snapshot")
@option("--dry-run", is_flag=True, help="Do not modify data")
@help_option(help="Show this message and exit")
@pass_obj
def archive(obj, folder: Path, comment: str | None, dry_run: bool):
    """Create snapshot of specified folder in archive repositories"""
    command = ArchiveCommand(config=obj["config"], borg=obj["borg"])
    command.run(folder, dry_run=dry_run, comment=comment)


@cli.command(section=SECTION_MAIN)
@option("--dry-run", is_flag=True, help="Do not modify data")
@help_option(help="Show this message and exit")
@pass_obj
def restore(obj, dry_run: bool):
    """Restore snapshot to current working directory (interactive)"""
    command = RestoreCommand(config=obj["config"], borg=obj["borg"], fzf=obj["fzf"])
    command.run(dry_run=dry_run)


@cli.command(section=SECTION_MAIN)
@option("--dry-run", is_flag=True, help="Do not modify data")
@help_option(help="Show this message and exit")
@pass_obj
def extract(obj, dry_run: bool):
    """Extract files / folders from snapshot (interactive)"""
    command = ExtractCommand(config=obj["config"], borg=obj["borg"], fzf=obj["fzf"])
    command.run(dry_run=dry_run)


@cli.command(section=SECTION_MAIN)
@option("--dry-run", is_flag=True, help="Do not modify data")
@help_option(help="Show this message and exit")
@pass_obj
def delete(obj, dry_run: bool):
    """Delete snapshot from repository (interactive) (DANGER)"""
    command = DeleteCommand(config=obj["config"], borg=obj["borg"], fzf=obj["fzf"])
    command.run(dry_run=dry_run)


@cli.command(section=SECTION_MAIN)
@option("--dry-run", is_flag=True, help="Do not modify data")
@help_option(help="Show this message and exit")
@pass_obj
def replace(obj, dry_run: bool):
    """
    Replace existing backup folders with restored ones (interactive) (DANGER)

    This command will delete the configured backup folders (!) and replace them
    with their counterparts in the current working directory. Please refer to the
    "Relativization" section in the README for details.
    """
    command = ReplaceCommand(config=obj["config"], fzf=obj["fzf"])
    command.run(dry_run=dry_run)


@cli.command(section=SECTION_UTILITY)
@help_option(help="Show this message and exit")
@pass_obj
def info(obj):
    """Show info about current configuration"""
    command = InfoCommand(config=obj["config"])
    command.run(obj["context"])


@cli.command(section=SECTION_UTILITY)
@help_option(help="Show this message and exit")
@pass_obj
def enable(obj):
    """Enable scheduled backups"""
    context: Context = obj["context"]
    Cron(context.profile).enable(
        "backup",
        context.easyborg_executable,
        context.borg_executable,
        context.fzf_executable,
        schedule="@hourly",
    )


@cli.command(section=SECTION_UTILITY)
@help_option(help="Show this message and exit")
@pass_obj
def disable(obj):
    """Disable scheduled backups"""
    context: Context = obj["context"]
    Cron(context.profile).disable()


@cli.command(section=SECTION_UTILITY)
@help_option(help="Show this message and exit")
@argument(
    "target",
    type=Choice(["log_file", "log_dir", "config_file", "config_dir"], case_sensitive=False),
)
@pass_obj
def open(obj, target: str):
    """Open easyborg file or folder"""
    command = OpenCommand(context=obj["context"])
    command.run(target)
