from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from easyborg.model import Config, Repository, RepositoryType


def load(path: Path) -> Config:
    """
    Load configuration from a TOML file.
    """
    try:
        with path.open("rb") as f:
            raw = tomllib.load(f)
    except FileNotFoundError:
        raise RuntimeError(f"Configuration file not found at: {path}")
    return _parse(raw, source=path)


def _parse(raw: dict[str, Any], source: Path) -> Config:
    folders = [Path(p) for p in raw.get("folders", [])]

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
        folders=folders,
        repos=repos,
    )
