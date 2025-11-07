from __future__ import annotations

from rich.console import Console
from rich.table import Table

_console = Console()

def info(msg: str) -> None:
    _console.print(f"[cyan]{msg}[/]")

def success(msg: str) -> None:
    _console.print(f"[bold green]{msg}[/]")

def warn(msg: str) -> None:
    _console.print(f"[yellow]{msg}[/]")

def error(msg: str) -> None:
    _console.print(f"[bold red]{msg}[/]")

def table(title: str, rows: list[tuple[str, ...]], headers: list[str]):
    t = Table(title=title)
    for h in headers:
        t.add_column(h)
    for row in rows:
        t.add_row(*row)
    _console.print(t)
