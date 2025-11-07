from __future__ import annotations

from rich import box
from rich.console import Console
from rich.table import Table

_console = Console()


def newline(count: int = 1) -> None:
    for i in range(count):
        _console.print("")


def info(msg: str) -> None:
    _console.print(f"{msg}", highlight=False)


def success(msg: str) -> None:
    _console.print(f"[bold green]{msg}[/]", highlight=False)


def warn(msg: str) -> None:
    _console.print(f"[yellow]{msg}[/]", highlight=False)


def error(msg: str) -> None:
    _console.print(f"[bold red]{msg}[/]", highlight=False)


def table(title: str, rows: list[tuple[str, ...]], headers=None, colors=None) -> None:
    if headers is None:
        headers = []
    if colors is None:
        colors = []
    show_headers = len(headers) > 0
    t = Table(
        title=title, min_width=80, title_justify="left", title_style="bold", box=box.ROUNDED, show_header=show_headers
    )
    for h in headers:
        t.add_column(h)
    for row in rows:
        t.add_row(*row)
    _console.print(t)
