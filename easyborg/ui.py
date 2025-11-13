from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from typing import TypeVar

from easyborg.model import ProgressEvent
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
from rich.style import Style

logger = logging.getLogger(__name__)
console = Console(highlight=False)

BAR_COLUMN = BarColumn(
    bar_width=10,
    pulse_style="cyan",
    complete_style="cyan",
    finished_style="white",
)

T = TypeVar("T")


def newline(count: int = 1) -> None:
    console.print("\n" * count, end="")


def out(msg: str, *, write_log=True, write_console=True) -> None:
    if write_console:
        console.print(msg)
    if write_log:
        logger.info(msg)


def success(msg: str) -> None:
    console.print(msg, style=Style(color="green"))
    logger.info("✅ " + msg)


def warn(msg: str) -> None:
    console.print(msg, style=Style(color="yellow"))
    logger.warning("⚠️ " + msg)


def error(msg: str) -> None:
    console.print(msg, style=Style(color="red"))
    logger.error("❌ " + msg)


def header(msg: str) -> None:
    console.print(f"{msg}:", style=Style(color="yellow", bold=True))


def progress(func: Callable[[], Iterator[ProgressEvent]]) -> T:
    """
    Display live Rich progress for a function that returns progress events.
    """
    with Progress(
        TextColumn("Processing"),
        BAR_COLUMN,
        TextColumn("{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        TextColumn("{task.description}", style=Style(color="yellow")),
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
    with Progress(
        TextColumn("Processing"),
        BAR_COLUMN,
        TextColumn("{task.description}", style=Style(color="yellow")),
        transient=True,
    ) as p:
        task_id = p.add_task("", total=None)
        for event in func():
            p.update(task_id, description=event.message)
