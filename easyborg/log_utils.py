import logging
from logging import Formatter, NullHandler
from logging.handlers import RotatingFileHandler
from pathlib import Path


def disable_all_logging():
    logger = logging.getLogger()
    logger.handlers.clear()
    logger.addHandler(NullHandler())


def enable_file_logging(log_file: Path, debug: bool) -> None:
    """
    Set up rotating file logging.
    """

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=1, encoding="utf-8")
    handler.setFormatter(Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.info("--------------------------------------------------------------------------------")
