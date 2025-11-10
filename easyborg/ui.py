from __future__ import annotations

import logging

from rich import box
from rich.console import Console
from rich.table import Table

_console = Console()
logger = logging.getLogger(__name__)


def newline(count: int = 1) -> None:
    _console.print("\n" * count, end="")


def info(msg: str) -> None:
    _console.print(msg, highlight=False)
    logger.info(msg)


def success(msg: str) -> None:
    msg = "✅ " + msg
    _console.print(msg, highlight=False)
    logger.info(msg)


def warn(msg: str) -> None:
    msg = "⚠️ " + msg
    _console.print(msg, highlight=False)
    logger.warning(msg)


def error(msg: str) -> None:
    msg = "❌ " + msg
    _console.print(msg, highlight=False)
    logger.error(msg)


def table(title: str, rows: list[tuple[str, ...]], headers=None) -> None:
    if headers is None:
        headers = []
    show_headers = len(headers) > 0
    t = Table(title=title, title_justify="left", title_style="bold", box=box.ROUNDED, show_header=show_headers)
    for h in headers:
        t.add_column(h)
    for row in rows:
        t.add_row(*row)
    _console.print(t)
