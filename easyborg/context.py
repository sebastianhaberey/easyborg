import os
import sys
from pathlib import Path

from easyborg.model import Context
from easyborg.process import get_full_executable_path
from platformdirs import PlatformDirs

APPNAME = "easyborg"

platform_dirs = PlatformDirs(APPNAME)


def load(
    profile: str,
    log_level: str,
    *,
    borg_executable: Path | None = None,
    fzf_executable: Path | None = None,
    easyborg_executable: Path | None = None,
) -> Context:
    # macOS: ~/Library/Logs/easyborg
    # Linux: $XDG_STATE_HOME/easyborg or ~/.local/state/easyborg
    log_dir = _get_log_dir(profile)

    # macOS: ~/Library/Application Support/easyborg
    # Linux: $XDG_CONFIG_HOME/easyborg or ~/.config/easyborg
    config_dir = _get_config_dir(profile)

    return Context(
        profile=profile,
        log_dir=log_dir,
        log_file=_get_log_file(log_dir),
        log_level=log_level,
        config_dir=config_dir,
        config_file=_get_config_file(config_dir),
        test=_is_test(),
        tty=_is_tty(),
        expert=_is_expert_mode(),
        borg_executable=borg_executable or _get_borg_executable(),
        fzf_executable=fzf_executable or _get_fzf_executable(),
        easyborg_executable=easyborg_executable,
    )


def _get_borg_executable() -> Path:
    return get_full_executable_path("borg")


def _get_fzf_executable() -> Path:
    return get_full_executable_path("fzf")


def _get_config_file(config_dir: Path) -> Path:
    return config_dir / f"{APPNAME}.toml"


def _get_config_dir(profile: str) -> Path:
    return Path(platform_dirs.user_config_dir) / profile


def _get_log_file(log_dir: Path) -> Path:
    return log_dir / f"{APPNAME}.log"


def _get_log_dir(profile: str) -> Path:
    return Path(platform_dirs.user_log_dir) / profile


def _is_test() -> bool:
    return "PYTEST_CURRENT_TEST" in os.environ


def _is_tty() -> bool:
    return sys.stdout.isatty()


def _is_expert_mode() -> bool:
    expert_mode = os.getenv(f"{APPNAME.upper()}_EXPERT_MODE")
    return expert_mode is not None and expert_mode.lower() in ["1", "true", "yes"]
