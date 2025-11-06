import typer

from easyborg.config import Config
from easyborg.core import Core

app = typer.Typer(help="easyborg - Borg for Dummies", add_completion=False, no_args_is_help=True)

config = Config.load()
core = Core(config)

@app.command()
def backup(
    repo: str | None = typer.Argument(
        None,
        help="Repository to back up (omit to back up all automatic repositories)",
    )
):
    """
    Create backup archive in one or more repositories.
    """

    if repo is None:
        print("Backing up all repositories")
        core.print_all()
        return
    else:
        print(f"Backing up into repository {repo}")
        core.print_all()
        return


@app.command()
def restore(
    repo: str | None = typer.Argument(None),
    archive: str | None = typer.Argument(None),
    target: str | None = typer.Option(None, "--target", "-t", help="Target directory (defaults to CWD)"),
):
    """
    Restore backup archive.
    """

    # Case 1 — No repo or archive → full interactive mode
    if repo is None and archive is None:
        print("Restoring")
        core.print_all()
        return

    # Case 2 — Repo given but no archive → ask user for archive
    if repo is not None and archive is None:
        print(f"Restoring from repository {repo}")
        core.print_all()
        return

    # Case 3 — Repo given and archive given -> go ahead
    print(f"Restoring from repository {repo} and archive {archive}")
    core.print_all()
