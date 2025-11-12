# easyborg/config.py
from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from easyborg.model import Config, Repository, RepositoryType


def load_config(path: Path | None = None) -> Config:
    """
    Load configuration from a TOML file.
    If path is None, load easyborg.toml in the current working directory.
    """
    if path is None:
        path = Path.cwd() / "easyborg.toml"

    try:
        raw = _load_toml(path)
    except FileNotFoundError:
        raise RuntimeError(f"Configuration file not found at: {path}")
    return _parse_config(raw, source=path)


def _parse_config(raw: dict[str, Any], source: Path) -> Config:
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


def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        return tomllib.load(f)
