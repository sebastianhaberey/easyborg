from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from typing import TypeVar

from easyborg.model import ProgressEvent
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn
from rich.style import Style

logger = logging.getLogger(__name__)
console = Console(highlight=False)

T = TypeVar("T")


def newline(count: int = 1) -> None:
    console.print("\n" * count, end="")


def out(msg: str, *, log=True) -> None:
    console.print(msg)
    if log:
        logger.info(msg)


def success(msg: str) -> None:
    # console.print("[bold][green]SUCCESS[/green][/bold] " + msg)
    console.print("✅ " + msg)
    logger.info("✅ " + msg)


def warn(msg: str) -> None:
    # console.print("[bold][yellow]WARNING[/yellow][/bold] " + msg)
    console.print("⚠️ " + msg)
    logger.warning("⚠️ " + msg)


def error(msg: str) -> None:
    # console.print("[bold][red]ERROR[/red][/bold] " + msg)
    console.print("❌ " + msg)
    logger.error("❌ " + msg)


def header(msg: str) -> None:
    console.print(f"[bold][yellow]{msg}[/yellow][/bold]:")


def progress(func: Callable[[], Iterator[ProgressEvent]], description: str | None = None) -> T:
    """
    Display live Rich progress for a function that returns progress events.
    """
    with Progress(
        TextColumn(f"{description}"),
        BarColumn(
            bar_width=10,
            complete_style="white",
            finished_style="white",
            pulse_style="black",
        ),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeRemainingColumn(elapsed_when_finished=True),
        refresh_per_second=10,
    ) as p:
        task_id = p.add_task("task", total=None)
        total = None
        for event in func():
            # print(f"EVENT: {event}")
            total = event.total
            p.update(
                task_id,
                total=total,
                completed=event.current,
            )
        # print("COMPLETED")
        p.update(task_id, total=total or 1, completed=total or 1, refresh=True)


def spinner(func: Callable[[], T] | None = None, description: str | None = None) -> T:
    """
    Display Rich spinner (indeterminate) for any operation.
    """
    with Progress(
        TextColumn(f"{description}"),
        SpinnerColumn(spinner_name="aesthetic", finished_text="", style=Style(color="cyan", dim=True), speed=0.5),
    ) as p:
        task_id = p.add_task("task", total=None)
        result = func()
        p.update(task_id, total=1, completed=1, refresh=True)
        return result
