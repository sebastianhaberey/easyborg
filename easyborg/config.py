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
            raw = tomllib.load(f)
    except FileNotFoundError:
        raise RuntimeError(f"Configuration file not found at: {path}")
    return _parse(raw, source=path)


def _parse(raw: dict[str, Any], source: Path) -> Config:
    backup_folders = [Path(p) for p in raw.get("backup_folders", [])]

    repos = {
        name: Repository(
            name=name,
            url=cfg["url"],
            type=RepositoryType(cfg["type"]),
        )
        for name, cfg in raw.get("repositories", {}).items()
    }

    return Config(
        source=source,
        backup_folders=backup_folders,
        repos=repos,
    )
