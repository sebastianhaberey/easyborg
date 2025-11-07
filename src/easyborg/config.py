from __future__ import annotations

import tomllib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class RepoType(str, Enum):
    BACKUP = "backup"
    ARCHIVE = "archive"


@dataclass(slots=True)
class Repo:
    name: str
    path: str
    type: RepoType


@dataclass(slots=True)
class Config:
    folders: list[Path]
    repos: dict[str, Repo]
    source: Path

    @staticmethod
    def load(path: Path | None = None) -> Config:
        if path is None:
            path = Path.cwd() / "easyborg.toml"

        raw = _load_toml(path)
        return _parse_config(raw, source=path)


def _parse_config(raw: dict[str, Any], source: Path) -> Config:
    folders = [Path(p).expanduser() for p in raw.get("folders", [])]

    repositories = {
        name: Repo(
            name=name,
            path=cfg["path"],
            type=RepoType(cfg["type"]),
        )
        for name, cfg in raw.get("repositories", {}).items()
    }

    return Config(
        folders=folders,
        repos=repositories,
        source=source,
    )


def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        return tomllib.load(f)
