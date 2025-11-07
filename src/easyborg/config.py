from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Repository:
    name: str
    path: Path
    type: str   # "backup" or "archive"


@dataclass
class Config:
    folders: list[Path]                           # <--- renamed
    repositories: dict[str, Repository]
    source: Path

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
    folders = [Path(p) for p in raw.get("folders", [])]

    repositories = {
        name: Repository(
            name=name,
            path=Path(cfg["path"]),
            type=cfg["type"],
        )
        for name, cfg in raw.get("repositories", {}).items()
    }

    return Config(
        folders=folders,
        repositories=repositories,
        source=source,
    )

def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        return tomllib.load(f)
