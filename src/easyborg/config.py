from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

from easyborg.util import deep_merge


def _in_development_mode() -> bool:
    """Return True if running inside a git checkout."""
    project_root = Path(__file__).resolve().parents[2]
    return (project_root / ".git").exists()


def load_config() -> dict[str, Any]:
    """
    Load easyborg configuration:

      1) EASYBORG_CONFIG (explicit override)
      2) If in development mode:
           config/default-easyborg.toml (base)
           config/dev-local.toml (git-ignored overrides)
      3) ~/.easyborg/easyborg.toml (user config)
    """

    # 1) Explicit override
    env_path = os.environ.get("EASYBORG_CONFIG")
    if env_path:
        p = Path(env_path).expanduser()
        if not p.exists():
            raise FileNotFoundError(f"$EASYBORG_CONFIG was set but file does not exist: {p}")
        return tomllib.loads(p.read_text())

    config: dict[str, Any] = {}

    if _in_development_mode():
        # Development template
        default_path = Path("./config/default-easyborg.toml")
        if default_path.exists():
            config = tomllib.loads(default_path.read_text())

        # Developer machine overrides (not committed)
        dev_local_path = Path("./config/dev-local.toml")
        if dev_local_path.exists():
            config = deep_merge(config, tomllib.loads(dev_local_path.read_text()))

    # User config (preferred for installed behavior)
    user_cfg_path = Path("~/.easyborg/easyborg.toml").expanduser()
    if user_cfg_path.exists():
        config = deep_merge(config, tomllib.loads(user_cfg_path.read_text()))

    return config
