from __future__ import annotations

import logging

import rich
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console(highlight=False)


def newline(count: int = 1) -> None:
    rich.print("\n" * count, end="")


def info(msg: str) -> None:
    console.print(msg)
    logger.info(msg)


def success(msg: str) -> None:
    console.print("[bold][green]SUCCESS[/green][/bold] " + msg)
    logger.info("✅ " + msg)


def warn(msg: str) -> None:
    console.print("[bold][yellow]WARNING[/yellow][/bold] " + msg)
    logger.warning("⚠️ " + msg)


def error(msg: str) -> None:
    console.print("[bold][red]ERROR[/red][/bold] " + msg)
    logger.error("❌ " + msg)


def header(msg: str) -> None:
    console.print(f"[bold][yellow]{msg}[/yellow][/bold]:")
