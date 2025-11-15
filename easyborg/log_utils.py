import logging
from logging import Formatter, NullHandler
from logging.handlers import RotatingFileHandler
from pathlib import Path


def initialize(log_file: Path, log_level: str, tty: bool, test: bool) -> None:
    """
    Initialize logging.

    a) test -> configure in pytest.ini
    b) TTY (interactive user) -> no logging
    c) non-TTY (cron / systemd) -> rotating file
    """
    if test:
        return

    logger = logging.getLogger()
    logger.handlers.clear()
    logger.setLevel(log_level)

    if tty:
        logger.addHandler(NullHandler())
        return

    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=1, encoding="utf-8")
    handler.setFormatter(Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)

    # mark beginning of new invocation
    logger.info("--------------------------------------------------------------------------------")
