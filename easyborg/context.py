import os
import sys
from pathlib import Path

from easyborg.model import Context
from platformdirs import PlatformDirs

APPNAME = "easyborg"


def load(profile: str) -> Context:
    dirs = PlatformDirs(APPNAME)

    # macOS: ~/Library/Logs/easyborg
    # Linux: $XDG_STATE_HOME/easyborg or ~/.local/state/easyborg
    log_dir = Path(dirs.user_log_dir) / profile
    log_file = log_dir / f"{APPNAME}.log"

    # macOS: ~/Library/Application Support/easyborg
    # Linux: $XDG_CONFIG_HOME/easyborg or ~/.config/easyborg
    config_dir = Path(dirs.user_config_dir) / profile
    config_file = config_dir / f"{APPNAME}.toml"

    return Context(
        profile=profile,
        log_dir=log_dir,
        log_file=log_file,
        log_level=_get_log_level(),
        config_dir=config_dir,
        config_file=config_file,
        test=_is_test(),
        tty=_is_tty(),
        expert=_is_expert_mode(),
    )


def _get_log_level() -> str | None:
    return os.environ.get(f"{APPNAME.upper()}_LOG_LEVEL", "INFO").upper()


def _is_test() -> bool:
    return "PYTEST_CURRENT_TEST" in os.environ


def _is_tty() -> bool:
    return sys.stdout.isatty()


def _is_expert_mode() -> bool:
    expert_mode = os.getenv(f"{APPNAME.upper()}_EXPERT_MODE")
    return expert_mode is not None and expert_mode.lower() in ["1", "true", "yes"]
