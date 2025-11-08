from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class RepositoryType(str, Enum):
    BACKUP = "backup"
    ARCHIVE = "archive"


@dataclass(frozen=True, slots=True)
class Snapshot:
    repo: Repository
    name: str

    def location(self) -> str:
        return f"{self.repo.url}::{self.name}"


@dataclass(slots=True)
class Repository:
    name: str
    url: str
    type: RepositoryType


@dataclass(slots=True)
class Config:
    source: Path
    folders: list[Path]
    repos: dict[str, Repository]
