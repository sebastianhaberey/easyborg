from __future__ import annotations

import logging
from collections.abc import Iterator

import rich
from easyborg.model import ProgressEvent
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn

logger = logging.getLogger(__name__)
console = Console(highlight=False)


def newline(count: int = 1) -> None:
    rich.print("\n" * count, end="")


def info(msg: str) -> None:
    console.print(msg)
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


def show_progress_bar(events: Iterator[ProgressEvent]) -> None:
    """
    Display live Rich progress for any iterator of progress events.
    """
    with Progress(
        BarColumn(
            bar_width=40,
            complete_style="white",
            finished_style="white",
            pulse_style="black",
        ),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeRemainingColumn(elapsed_when_finished=True),
        refresh_per_second=10,
    ) as progress:
        task_id = progress.add_task("task")
        total = None
        for event in events:
            # print(f"EVENT: {event}")
            total = event.total
            progress.update(
                task_id,
                total=total,
                completed=event.current,
            )
        # print("COMPLETED")
        progress.update(task_id, total=total or 1, completed=total or 1, refresh=True)
