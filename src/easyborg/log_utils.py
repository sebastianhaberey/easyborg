import logging
from logging import Formatter, NullHandler
from logging.handlers import RotatingFileHandler
from pathlib import Path

from easyborg.context import platform_dirs


def disable_logging():
    logger = logging.getLogger()
    logger.handlers.clear()
    logger.addHandler(NullHandler())


def enable_file_logging(log_file: Path, debug: bool) -> None:
    """
    Set up rotating file logging.
    """

    logger = logging.getLogger()
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=1, encoding="utf-8")
    handler.setFormatter(Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)


def get_log_file(log_dir: Path) -> Path:
    """
    Return platform-specific log file.
    """
    return log_dir / "easyborg.log"


def get_log_dir(profile: str) -> Path:
    """
    Return platform-specific log directory.

    macOS: ~/Library/Logs/easyborg
    Linux: $XDG_STATE_HOME/easyborg or ~/.local/state/easyborg
    """
    return Path(platform_dirs.user_log_dir) / profile
