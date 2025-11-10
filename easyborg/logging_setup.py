import logging
import logging.handlers
import os
import sys
from pathlib import Path

CURRENT_LOG_FILE: Path | None = None
CURRENT_LOG_LEVEL: str | None = None


def setup_logging(test_mode: bool = False):
    """
    Configure logging behavior.

    a) Unit test (pytest)      → No logging
    b) Non-TTY (cron/systemd)  → Rotating file
    c) TTY (interactive user)  → No logging
    """
    global CURRENT_LOG_FILE, CURRENT_LOG_LEVEL

    level = logging.getLevelName(os.environ.get("EASYBORG_LOG_LEVEL", "INFO").upper())

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers.clear()

    is_tty = sys.stdout.isatty()
    is_test = test_mode or "PYTEST_CURRENT_TEST" in os.environ

    if is_test or is_tty:
        logger.addHandler(logging.NullHandler())
        return

    log_dir = get_log_dir()
    log_file = log_dir / "easyborg.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=1, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)

    CURRENT_LOG_FILE = log_file
    CURRENT_LOG_LEVEL = logging.getLevelName(level)


def get_log_dir() -> Path:
    """
    Return log dir for easyborg.

    macOS:  ~/Library/Logs/easyborg
    Linux:  ~/.local/state/easyborg (or ${XDG_STATE_HOME}/easyborg)
    Windows: %LOCALAPPDATA%/easyborg

    EASYBORG_LOG_DIR overrides all if set
    """

    env_log_dir = os.environ.get("EASYBORG_LOG_DIR")
    if env_log_dir:
        return Path(env_log_dir).expanduser()

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Logs" / "easyborg"

    elif sys.platform.startswith("linux"):
        xdg_state = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
        return xdg_state / "easyborg"

    elif sys.platform.startswith("win"):
        local_appdata = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
        return local_appdata / "easyborg"

    raise RuntimeError(f"Unsupported platform: {sys.platform}")


def get_current_log_file() -> Path | None:
    return CURRENT_LOG_FILE


def get_current_log_level() -> str | None:
    return CURRENT_LOG_LEVEL
