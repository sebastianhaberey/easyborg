from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def newline(count: int = 1) -> None:
    print("\n" * count, end="")


def info(msg: str) -> None:
    print(msg)
    logger.info(msg)


def success(msg: str) -> None:
    msg = "✅ " + msg
    print(msg)
    logger.info(msg)


def warn(msg: str) -> None:
    msg = "⚠️ " + msg
    print(msg)
    logger.warning(msg)


def error(msg: str) -> None:
    msg = "❌ " + msg
    print(msg)
    logger.error(msg)
