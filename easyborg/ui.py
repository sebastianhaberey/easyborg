from __future__ import annotations

import logging
import sys
from collections.abc import Callable, Iterator
from typing import TypeVar

from easyborg.model import ProgressEvent
from rich.console import Console
from rich.progress import BarColumn, Progress, Task, TextColumn, TimeRemainingColumn
from rich.style import StyleType
from rich.text import Text

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
        BAR_COLUMN,
        TextColumn("{task.percentage:>3.0f}%"),
        StylableTimeRemainingColumn(style="yellow"),
        TextColumn("{task.description}", style="white"),
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
        BAR_COLUMN,
        StylableTimeRemainingColumn(style="yellow"),
        TextColumn("{task.description}", style="white"),
        transient=True,
    ) as p:
        task_id = p.add_task("", total=None)
        for event in func():
            p.update(task_id, description=event.message)


def is_tty() -> bool:
    return sys.stdout.isatty()


class StylableTimeRemainingColumn(TimeRemainingColumn):
    def __init__(self, style=StyleType):
        super().__init__()
        self.style = style

    def render(self, task: Task) -> Text:
        """Show time remaining."""
        task_time = task.time_remaining

        if task.total is None:
            return Text("", style=self.style)

        if task_time is None:
            return Text("--:--" if self.compact else "-:--:--", style=self.style)

        # Based on https://github.com/tqdm/tqdm/blob/master/tqdm/std.py
        minutes, seconds = divmod(int(task_time), 60)
        hours, minutes = divmod(minutes, 60)

        formatted = f"{hours:d}:{minutes:02d}:{seconds:02d}"

        return Text(formatted, style=self.style)
