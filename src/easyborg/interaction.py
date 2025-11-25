from collections.abc import Iterator
from pathlib import Path

from easyborg import ui
from easyborg.borg import Borg
from easyborg.fzf import Fzf, SortOrder
from easyborg.model import Config, ProgressEvent, Repository, Snapshot
from easyborg.util import remove_redundant_paths


def select_repo(fzf: Fzf, config: Config) -> Repository | None:
    ui.info("Select repository")

    selected = fzf.select_items(
        config.repos.values(),
        key=lambda r: r.name,
    )

    if not selected:
        ui.selected(None)
        return None

    repo = selected[0]
    ui.selected(repo.name)

    return repo


def select_snapshot(borg: Borg, fzf: Fzf, repo: Repository) -> Snapshot | None:
    ui.info("Select snapshot")

    snapshots: list[Snapshot] | None = None

    def list_snapshots(repo: Repository) -> Iterator[ProgressEvent]:
        nonlocal snapshots
        snapshots = borg.list_snapshots(repo)
        return iter([])

    ui.spinner(
        lambda: list_snapshots(repo),
        message="Listing snapshots",
    )

    selected = fzf.select_items(
        snapshots,
        key=lambda s: f"{s.name} — {s.comment}" if s.comment else s.name,
        sort_order=SortOrder.DESCENDING,
    )

    if not selected:
        ui.selected(None)
        return None

    snapshot = selected[0]
    ui.selected(snapshot.full_name())

    return snapshot


def select_items(borg: Borg, fzf: Fzf, snapshot: Snapshot) -> list[Path] | None:
    ui.info("Select items")

    selected = fzf.select_strings(
        map(str, borg.list_contents(snapshot)),
        multi=True,
        show_info=True,
    )

    if not selected:
        ui.selected(None)
        return None

    selected_paths = [Path(s) for s in selected]
    selected_paths = remove_redundant_paths(selected_paths)
    ui.selected(selected_paths)

    return selected_paths


def confirm(fzf: Fzf, message: str, *, danger: bool = False) -> bool | None:
    if danger:
        ui.info(f"[red][bold]DANGER[/red][/bold] {message}")
    else:
        ui.info(message)

    response = fzf.select_strings(["NO", "MAYBE", "YES"], danger=danger)

    if len(response) == 0:
        ui.selected(None)
        return None

    ui.selected(response[0], danger=danger)
    return response[0] == "YES"


def select_folders(fzf: Fzf, folders: list[Path]) -> list[Path] | None:
    ui.info("Select folders")
    selected_folders = fzf.select_items(
        folders,
        str,
        multi=True,
    )

    if not selected_folders:
        ui.selected(None)
        return None

    ui.selected(selected_folders)
    return selected_folders
