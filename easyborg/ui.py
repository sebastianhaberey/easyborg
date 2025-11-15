from __future__ import annotations

import logging
import sys
from collections.abc import Callable, Iterable, Iterator, Sequence
from pathlib import Path
from typing import TypeVar

from easyborg.model import ProgressEvent
from rich import box
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.theme import Theme

T = TypeVar("T")
logger = logging.getLogger(__name__)

theme = Theme(
    {
        "progress.remaining": "yellow",
        "progress.elapsed": "yellow",
    }
)

progress_bar_column = BarColumn(
    bar_width=10,
    pulse_style="cyan",
    complete_style="cyan",
    finished_style="white",
)

console = Console(highlight=False, theme=theme)


def newline(count: int = 1) -> None:
    console.print("\n" * count, end="")


def out(msg: str, *, write_log=True) -> None:
    console.print(msg)
    if write_log:
        logger.info(msg)


def success(msg: str) -> None:
    console.print(msg, style="green bold")
    logger.info("✅ " + msg)


def warn(msg: str) -> None:
    console.print(msg, style="yellow bold")
    logger.warning("⚠️ " + msg)


def error(msg: str) -> None:
    console.print(msg, style="red bold")
    logger.error("❌ " + msg)


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
        TextColumn("Processing"),
        progress_bar_column,
        TextColumn("{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        TextColumn("{task.description}", style="white"),
        console=console,
        transient=True,
    ) as p:
        task_id = p.add_task("", total=None)
        for event in func():
            # print(f"EVENT: {event}")
            p.update(
                task_id,
                total=event.total or None,
                completed=event.current or None,
                description=event.message or None,
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
        TextColumn("Processing"),
        progress_bar_column,
        TimeRemainingColumn(),
        TextColumn("{task.description}", style="white"),
        console=console,
        transient=True,
    ) as p:
        task_id = p.add_task("", total=None)
        for event in func():
            p.update(task_id, description=event.message)


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
        title=title + ":",
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
