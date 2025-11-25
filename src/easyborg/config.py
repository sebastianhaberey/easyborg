from __future__ import annotations

import shutil
import tomllib
from importlib import resources
from pathlib import Path
from typing import Any

from easyborg.model import Config, Repository, RepositoryType


def load(path: Path) -> Config:
    """
    Load configuration from a TOML file.
    """

    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with resources.as_file(resources.files("easyborg.resources")) as source:
            shutil.copy(source / "template-easyborg.toml", path)

    try:
        with path.open("rb") as f:
            cfg = tomllib.load(f)
    except FileNotFoundError:
        raise RuntimeError(f"Configuration file not found at: {path}")
    return _parse(cfg)


def _parse(cfg: dict[str, Any]) -> Config:
    repos = {
        name: Repository(
            name=name,
            url=cfg_repo.get("url", None),
            type=RepositoryType(cfg_repo.get("type", None)),
            compact_probability=cfg_repo.get("compact_probability", 0.10),
            env=cfg_repo.get("environment", {}),
        )
        for name, cfg_repo in cfg.get("repositories", {}).items()
    }

    return Config(
        backup_paths=[Path(p) for p in cfg.get("backup_paths", [])],
        repos=repos,
        env=cfg.get("environment", {}),
    )
