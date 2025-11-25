import os
import sys
from pathlib import Path

from platformdirs import PlatformDirs

from easyborg.model import Context
from easyborg.process import get_full_executable_path

platform_dirs = PlatformDirs("easyborg")


def create(
    *,
    profile: str,
    log_dir: Path,
    log_file: Path,
    debug: bool,
    headless: bool,
    easyborg_executable: Path,
    borg_executable: Path | None = None,
    fzf_executable: Path | None = None,
) -> Context:
    # macOS: ~/Library/Application Support/easyborg
    # Linux: $XDG_CONFIG_HOME/easyborg or ~/.config/easyborg
    config_dir = _get_config_dir(profile)

    return Context(
        profile=profile,
        log_dir=log_dir,
        log_file=log_file,
        debug=debug,
        headless=headless,
        config_dir=config_dir,
        config_file=_get_config_file(config_dir),
        test=_is_test(),
        tty=_is_tty(),
        expert=_is_expert_mode(),
        easyborg_executable=easyborg_executable,
        borg_executable=borg_executable or _get_borg_executable(),
        fzf_executable=fzf_executable or _get_fzf_executable(),
        python_executable=_get_python_executable(),
        real_python_executable=_get_real_python_executable(),
    )


def _get_borg_executable() -> Path:
    try:
        return get_full_executable_path("borg")
    except Exception:
        raise RuntimeError("Could could not locate Borg executable. Please make sure Borg is installed.")


def _get_fzf_executable() -> Path:
    try:
        return get_full_executable_path("fzf")
    except Exception:
        raise RuntimeError("Could could not locate fzf executable. Please make sure fzf is installed.")


def _get_config_file(config_dir: Path) -> Path:
    return config_dir / "easyborg.toml"


def _get_config_dir(profile: str) -> Path:
    return Path(platform_dirs.user_config_dir) / "profiles" / profile


def _is_test() -> bool:
    return "PYTEST_CURRENT_TEST" in os.environ


def _is_tty() -> bool:
    return sys.stdout.isatty()


def _is_expert_mode() -> bool:
    expert_mode = os.getenv("EASYBORG_EXPERT_MODE")
    return expert_mode is not None and expert_mode.lower() in ["1", "true", "yes"]


def _get_python_executable() -> Path:
    return Path(sys.executable)


def _get_real_python_executable() -> Path:
    return Path(os.path.realpath(sys.executable))
