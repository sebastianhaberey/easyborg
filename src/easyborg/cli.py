import logging
import os
from pathlib import Path

import cloup
from click import help_option, pass_obj, version_option
from cloup import HelpFormatter, HelpTheme, Style, argument, command, group, option, pass_context

import easyborg
from easyborg import config, log_utils, ui
from easyborg.borg import Borg
from easyborg.core import Core
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
        max_width=120,
    ),
)

# TODO SH eliminate this constant and remove protected method access
# noinspection PyProtectedMember
EXPERT_MODE: bool = easyborg.context._is_expert_mode()

# TODO SH find a better way to pass debug flag to exception handling
DEBUG_MODE: bool = False


@group(help="Easyborg – Borg for Dummies", context_settings=CONTEXT_SETTINGS)
@version_option(prog_name="Easyborg", help="Show version information", message="%(prog)s version %(version)s")
@help_option(help="Show this page and exit")
@option(
    "--profile",
    type=str,
    hidden=not EXPERT_MODE,
    help="Select configuration profile (expert)",
    default="default",
)
@option(
    "--debug",
    type=bool,
    is_flag=True,
    hidden=not EXPERT_MODE,
    help="Enable debug mode (expert)",
)
@option(
    "--scheduled",
    type=bool,
    is_flag=True,
    hidden=not EXPERT_MODE,
    help="Signal easyborg that it is called by scheduler (expert)",
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
    scheduled: bool,
    borg_executable: Path | None,
    fzf_executable: Path | None,
) -> None:
    global DEBUG_MODE
    DEBUG_MODE = debug

    ctx.ensure_object(dict)

    easyborg_executable = ctx.obj.pop("easyborg_executable", None)  # move from Click context to Easyborg context

    context = easyborg.context.create(
        profile,
        debug,
        scheduled,
        borg_executable=borg_executable,
        fzf_executable=fzf_executable,
        easyborg_executable=easyborg_executable,
    )
    ctx.obj["context"] = context

    if scheduled:
        log_utils.enable_file_logging(context.log_file, context.debug)
    else:
        ui.quiet(False)

    configuration = config.load(context.config_file)
    os.environ.update(configuration.env)
    ctx.obj["configuration"] = configuration

    core = Core(
        configuration,
        Borg(executable=context.borg_executable),
        Fzf(executable=context.fzf_executable),
    )
    ctx.obj["core"] = core

    cron = Cron(profile)
    ctx.obj["cron"] = cron


@command()
@option("--dry-run", is_flag=True, help="Do not modify data.")
@pass_obj
def backup(obj, dry_run: bool):
    """Create snapshot of configured folders in backup repositories"""
    obj["core"].backup(dry_run=dry_run)


@command()
@argument("folder", type=cloup.Path(path_type=Path, exists=True), help="Folder to backup.")
@option("--comment", help="Add comment to the created snapshot.")
@option("--dry-run", is_flag=True, help="Do not modify data.")
@pass_obj
def archive(obj, folder: Path, comment: str | None, dry_run: bool):
    """Create snapshot of specified folder in archive repositories (interactive)"""
    obj["core"].archive(folder, dry_run=dry_run, comment=comment)


@command()
@option("--dry-run", is_flag=True, help="Do not modify data.")
@pass_obj
def restore(obj, dry_run: bool):
    """Restore snapshot to current working directory (interactive)"""
    obj["core"].restore(dry_run=dry_run)


@command()
@option("--dry-run", is_flag=True, help="Do not modify data.")
@pass_obj
def extract(obj, dry_run: bool):
    """Extract files / folders from snapshot (interactive)"""
    obj["core"].extract(dry_run=dry_run)


@command()
@option("--dry-run", is_flag=True, help="Do not modify data.")
@pass_obj
def delete(obj, dry_run: bool):
    """Delete snapshot from repository (interactive)"""
    obj["core"].delete(dry_run=dry_run)


@command()
@pass_obj
def info(obj):
    """Show info about the current configuration"""
    obj["core"].info(obj["context"])


@command()
@pass_obj
def enable(obj):
    """Enable scheduled backups"""
    context: Context = obj["context"]
    obj["cron"].enable(
        "backup",
        context.easyborg_executable,
        context.borg_executable,
        context.fzf_executable,
        schedule="@hourly",
    )


@command()
@pass_obj
def disable(obj):
    """Disable scheduled backups"""
    obj["cron"].disable()


cli.section(
    "Main Commands",
    backup,
    archive,
    restore,
    extract,
    delete,
)

cli.section(
    "Utility Commands",
    info,
    enable,
    disable,
)
