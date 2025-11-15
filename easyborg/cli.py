from pathlib import Path

import cloup
import easyborg
from click import pass_obj, version_option
from cloup import HelpFormatter, HelpTheme, Style, argument, command, group, option, pass_context
from easyborg import config, context, log_utils
from easyborg.core import Core
from easyborg.cron import Cron

CONTEXT_SETTINGS = cloup.Context.settings(
    formatter_settings=HelpFormatter.settings(
        theme=HelpTheme(
            invoked_command=Style(fg="magenta", bold=True),
            heading=Style(fg="yellow", bold=True),
            col1=Style(fg="cyan", bold=True),
        ),
    ),
)

# TODO SH eliminate this constant, remove protected access
# noinspection PyProtectedMember
EXPERT_MODE = context._is_expert_mode()


@group(help="Easyborg – Borg for Dummies", context_settings=CONTEXT_SETTINGS)
@version_option(package_name="easyborg")
@option(
    "--profile",
    type=str,
    hidden=not EXPERT_MODE,
    help="Select configuration profile (expert-only).",
    default="default",
)
@pass_context
def cli(ctx: cloup.Context, profile: str):
    ctx.ensure_object(dict)

    context = easyborg.context.load(profile)
    ctx.obj["context"] = context

    log_utils.initialize(context.log_file, context.log_level, context.tty, context.test)

    configuration = config.load(context.config_file)
    ctx.obj["configuration"] = configuration

    core = Core(configuration)
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
    """Create snapshot of specified folder in archive repositories"""
    obj["core"].archive(folder, dry_run=dry_run, comment=comment)


@command()
@option("--dry-run", is_flag=True, help="Do not modify data.")
@pass_obj
def restore(obj, dry_run: bool):
    """Restore snapshot to current working directory"""
    obj["core"].restore(dry_run=dry_run)


@command()
@option("--dry-run", is_flag=True, help="Do not modify data.")
@pass_obj
def extract(obj, dry_run: bool):
    """Interactively extract files / folders from snapshot"""
    obj["core"].extract(dry_run=dry_run)


@command()
@option("--dry-run", is_flag=True, help="Do not modify data.")
@pass_obj
def delete(obj, dry_run: bool):
    """Interactively delete snapshot from repository"""
    obj["core"].delete(dry_run=dry_run)


@command()
@pass_obj
def info(obj):
    """Output info about the current configuration"""
    obj["core"].info(obj["context"])


@command()
@pass_obj
def enable(obj):
    """Enable automatic backups (runs 'easyborg backup' hourly)"""
    obj["cron"].enable("easyborg backup", "@hourly")


@command()
@pass_obj
def disable(obj):
    """Disable automatic backups"""
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
