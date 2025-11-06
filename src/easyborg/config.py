from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class DirectoryGroup:
    name: str
    paths: list[str]


@dataclass(slots=True)
class Repository:
    name: str
    path: str
    type: str   # "automatic" or "manual"
    directory_groups: list[str]


@dataclass
class Config:
    directories: dict[str, DirectoryGroup]
    repositories: dict[str, Repository]
    source: Path  # Which file was actually loaded

    @staticmethod
    def load(path: Path | None = None) -> Config:
        """
        Load configuration.

        If `path` is provided (test usage), load only that file.
        Otherwise load from config/easyborg.toml inside the project.
        """
        if path is None:
            path = Path(__file__).resolve().parents[2] / "config" / "easyborg.toml"

        raw = _load_toml(path)
        return _parse_config(raw, source=path)

def _parse_config(raw: dict[str, Any], source: Path) -> Config:
    directories = {
        name: DirectoryGroup(name=name, paths=cfg["paths"])
        for name, cfg in raw.get("directories", {}).items()
    }

    repositories = {
        name: Repository(
            name=name,
            path=cfg["path"],
            type=cfg.get("type", "manual"),
            directory_groups=cfg.get("directory_groups", []),
        )
        for name, cfg in raw.get("repositories", {}).items()
    }

    return Config(
        directories=directories,
        repositories=repositories,
        source=source,
    )

def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        return tomllib.load(f)
