from pathlib import Path

from easyborg.borg import Borg
from easyborg.fzf import Fzf, SortOrder
from easyborg.model import Config, Repository, Snapshot


def select_repo(fzf: Fzf, config: Config) -> Repository | None:
    repos = fzf.select_items(
        config.repos.values(),
        key=lambda r: r.name,
    )
    return repos[0] if repos else None


def select_snapshot(fzf: Fzf, snapshots: list[Snapshot]) -> Snapshot | None:
    snapshot = fzf.select_items(
        snapshots,
        key=lambda s: f"{s.name} — {s.comment}" if s.comment else s.name,
        sort_order=SortOrder.DESCENDING,
    )
    return snapshot[0] if snapshot else None


def select_paths(borg: Borg, fzf: Fzf, snapshot: Snapshot) -> list[Path]:
    path_strings = fzf.select_strings(
        map(str, borg.list_contents(snapshot)),
        multi=True,
        show_info=True,
    )
    return [Path(s) for s in path_strings]
