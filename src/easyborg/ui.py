from __future__ import annotations

import logging
import sys
from collections.abc import Callable, Iterable, Iterator, Sequence
from pathlib import Path
from typing import TypeVar

import click
import cloup
import rich
from rich import box
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn
from rich.style import StyleType
from rich.table import Table
from rich.theme import Theme

from easyborg.model import ProgressEvent

INDENT_SIZE = 2

T = TypeVar("T")
logger = logging.getLogger(__name__)

theme = Theme(
    {
        "progress.remaining": "bold cyan",
        "progress.elapsed": "bold cyan",
    }
)

progress_bar_column = BarColumn(
    bar_width=10,
    pulse_style="cyan",
    complete_style="cyan",
    finished_style="bold cyan",
)

console = Console(highlight=False, theme=theme, quiet=True)  # start out quiet, enable later

# CONSOLE PLUS LOGGING


def info(msg: str) -> None:
    console.print(msg)
    logger.info(msg)


def success(msg: str, secondary: str = None) -> None:
    if secondary:
        console.print(f"[green][bold]{msg}:[/bold][/green] {secondary}")
        logger.info(f"✅ {msg}: {secondary}")
    else:
        console.print(f"[green][bold]{msg}[/bold][/green]")
        logger.info(f"✅ {msg}")


def warn(msg: str, secondary: str = None) -> None:
    if secondary:
        console.print(f"[yellow][bold]{msg}:[/bold][/yellow] {secondary}")
        logger.info(f"⚠️ {msg}: {secondary}")
    else:
        console.print(f"[yellow][bold]{msg}[/bold][/yellow]")
        logger.info(f"⚠️ {msg}")


def error(msg: str, secondary: str = None) -> None:
    if secondary:
        console.print(f"[red][bold]{msg}:[/bold][/red] {secondary}")
        logger.info(f"❌ {msg}: {secondary}")
    else:
        console.print(f"[red][bold]{msg}[/bold][/red]")
        logger.info(f"❌ {msg}")


def exception(e: Exception) -> None:
    error(e.__class__.__name__, str(e))


def stacktrace(message: str) -> None:
    console.print_exception(suppress=[click, cloup, rich], extra_lines=0)
    logger.exception("❌ " + message)


# CONSOLE ONLY


def newline(count: int = 1) -> None:
    console.print("\n" * count, end="")


def display(msg: str, *, indent: int = 0, style: StyleType = None) -> None:
    console.print((" " * indent * INDENT_SIZE) + msg, style=style)


def header(msg: str) -> None:
    console.print(f"{msg}:", style="yellow bold")


def progress(func: Callable[[], Iterator[ProgressEvent]]) -> None:
    """
    Display live Rich progress for a function that returns progress events.
    """
    if not is_tty():
        list(func())
        return

    with Progress(
        progress_bar_column,
        # TextColumn("{task.percentage:>3.0f}%"),  # don't need it currently as Borg's messages contain percentage
        TimeRemainingColumn(),
        TextColumn("{task.description}"),
        console=console,
        transient=True,
    ) as p:
        task_id = p.add_task("Processing", total=None)
        for event in func():
            # print(f"EVENT: {event}")
            p.update(
                task_id,
                total=event.total or None,
                completed=event.current or None,
                description=trim(event.message, console.size.width - 20) if event.message else None,  # total length 120
            )
        # print("COMPLETED")


def spinner(func: Callable[[], Iterator[ProgressEvent]]) -> None:
    """
    Display Rich spinner (indeterminate) for any operation.
    """
    if not is_tty():
        list(func())
        return

    with Progress(
        SpinnerColumn(style="bold cyan"),
        TextColumn("{task.description}", style="white"),
        console=console,
        transient=True,
    ) as p:
        task_id = p.add_task("Processing", total=None)
        for event in func():
            p.update(task_id, description=trim(event.message, console.size.width - 2))


def is_tty() -> bool:
    return sys.stdout.isatty()


def table(
    rows: Iterable[Sequence[str | object]] = (),
    *,
    title: str | None = None,
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
        title=title + ":" if title else None,
        title_style="yellow bold",
        title_justify="left",
        show_header=bool(headers),
        box=box,
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

    console.print(table)


def link_path(path: Path) -> str:
    return f"[link={path.as_uri()}]{path}[/link]"


def render_dict(value: dict[str, str], *, separator=", ") -> str:
    return separator.join(f"{k}: [cyan][bold]{v}[/bold][/cyan]" for k, v in value.items())


def trim(s: str, max_len: int) -> str:
    return s if len(s) <= max_len else s[: max_len - 1] + "…"


def quiet(value: bool) -> None:
    global console
    console.quiet = value
