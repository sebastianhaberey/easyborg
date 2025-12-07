from __future__ import annotations

import logging
import sys
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any, TypeVar

import click
import cloup
import rich
from rich import box
from rich.console import Console
from rich.padding import Padding
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn
from rich.style import Style, StyleType
from rich.table import Table
from rich.theme import Theme

from easyborg.model import ProgressEvent
from easyborg.theme import StyleId, SymbolId, theme

STYLES = theme().styles
SYMBOLS = theme().symbols

INDENT_SIZE = 2

T = TypeVar("T")
logger = logging.getLogger(__name__)

console_theme = Theme(
    {
        "progress.remaining": Style(),
        "progress.elapsed": Style(),
        "bar.pulse": Style(),
        "bar.complete": STYLES[StyleId.PRIMARY],
        "bar.finished": STYLES[StyleId.PRIMARY],
        "bar.back": STYLES[StyleId.GRAY],
    }
)

console = Console(highlight=False, theme=console_theme, soft_wrap=True)

# CONSOLE PLUS LOGGING


def info(msg: str, danger: bool = False) -> None:
    if danger:
        console.print(SYMBOLS[SymbolId.DANGER], style=STYLES[StyleId.DANGER], end="")
        console.print(str(msg))
    else:
        console.print(msg)
    logger.info(msg)


def success(msg: str, secondary: str = None) -> None:
    if secondary:
        console.print(msg, style=STYLES[StyleId.SUCCESS], end="")
        console.print(": ", secondary)
        logger.info(f"✅ {msg}: {secondary}")
    else:
        console.print(msg, style=STYLES[StyleId.SUCCESS])
        logger.info(f"✅ {msg}")


def warn(msg: str, secondary: str = None) -> None:
    if secondary:
        console.print(msg, style=STYLES[StyleId.WARNING], end="")
        console.print(": ", secondary)
        logger.info(f"⚠️ {msg}: {secondary}")
    else:
        console.print(msg, style=STYLES[StyleId.WARNING])
        logger.info(f"⚠️ {msg}")


def error(msg: str, secondary: str = None) -> None:
    newline()
    if secondary:
        console.print(msg, style=STYLES[StyleId.ERROR], end="")
        console.print(": ", secondary)
        logger.info(f"❌ {msg}: {secondary}")
    else:
        console.print(msg, style=STYLES[StyleId.ERROR])
        logger.info(f"❌ {msg}")


def exception(e: Exception) -> None:
    error(e.__class__.__name__, str(e))


def stacktrace(message: str) -> None:
    console.print_exception(suppress=[click, cloup, rich], extra_lines=0)
    logger.exception("❌ " + message)


def selected(value: Any, danger: bool = False) -> None:
    if not isinstance(value, list):
        value = [value]
    for item in value:
        if danger:
            console.print(SYMBOLS[SymbolId.PROMPT], style=STYLES[StyleId.DANGER], end="")
            console.print(str(item))
        else:
            console.print(SYMBOLS[SymbolId.PROMPT], style=STYLES[StyleId.PRIMARY], end="")
            console.print(str(item))


def abort() -> None:
    newline()
    warn("Aborted")


# CONSOLE ONLY


def newline(count: int = 1) -> None:
    console.print("\n" * count, end="")


def display(msg: str, *, indent: int = 0, style: StyleType = None, danger: bool = False) -> None:
    console.print(" " * indent * INDENT_SIZE, end="")
    if danger:
        console.print(SYMBOLS[SymbolId.DANGER], style=STYLES[StyleId.DANGER], end="")
    console.print(msg, style=style)


def header(msg: str, *, first=False) -> None:
    if not first:
        newline()
    console.print(f"{msg}:", style=STYLES[StyleId.HEADER])


def progress(func: Callable[[], Iterator[ProgressEvent]], *, message: str = "Processing") -> None:
    """
    Display live Rich progress for a function that returns progress events.
    """
    if not is_tty():
        list(func())
        return

    with Progress(
        BarColumn(bar_width=10),
        TimeRemainingColumn(),
        TextColumn("{task.description}"),
        console=console,
        transient=True,
    ) as p:
        task_id = p.add_task(message, start=True)
        for event in func():
            # print(f"EVENT: {event}")
            p.update(
                task_id,
                total=event.total or None,
                completed=event.current or None,
                description=trim(event.message, console.size.width - 20) if event.message else None,
            )
        # print("COMPLETED")


def spinner(func: Callable[[], Iterator[ProgressEvent]], *, message: str = "Processing") -> None:
    """
    Display Rich spinner (indeterminate) for any operation.
    """
    if not is_tty():
        list(func())
        return

    with Progress(
        SpinnerColumn(style=STYLES[StyleId.PRIMARY]),
        TextColumn("{task.description}"),
        console=console,
        transient=True,
    ) as p:
        task_id = p.add_task(message, total=None)
        for event in func():
            p.update(task_id, description=trim(event.message, console.size.width - 2))


def is_tty() -> bool:
    return sys.stdout.isatty()


def table(
    rows: Iterable[Sequence[str | object]],
    *,
    headers: Sequence[str] | None = None,
    column_colors: Sequence[str | None] = (),
    box=box.SIMPLE_HEAD,
) -> None:
    """
    Print a table to the console using Rich.
    """
    # Infer number of columns from headers / first row
    num_columns = len(headers) if headers else len(next(iter(rows)))

    # Pad column colors to match number of columns
    column_colors = list(column_colors) + [None] * (num_columns - len(column_colors))

    table = Table(
        show_header=bool(headers),
        box=box,
        show_edge=False,
    )

    # Add headers (unstyled)
    if headers:
        for header in headers:
            table.add_column(header)
    else:
        for _ in range(num_columns):
            table.add_column("")

    # Add rows with per-column formatting
    for row in rows:
        formatted_row = []
        for cell, color in zip(row, column_colors):
            cell_str = str(cell)
            if color:
                cell_str = f"[{color}]{cell_str}[/{color}]"
            formatted_row.append(cell_str)
        table.add_row(*formatted_row)

    console.print(Padding(table, (0, 1, 0, 1)))


def link_path(path: Path) -> str:
    return f"{path}"


def render_mapping(value: Mapping[str, str], *, separator=", ") -> str:
    return separator.join(f"{k}: {v}" for k, v in value.items())


def trim(s: str, max_len: int) -> str:
    return s if len(s) <= max_len else s[: max_len - 1] + "…"


def disable() -> None:
    global console
    console.quiet = True
