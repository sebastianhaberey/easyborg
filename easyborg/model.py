from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class RepositoryType(str, Enum):
    BACKUP = "backup"
    ARCHIVE = "archive"


@dataclass(frozen=True, slots=True)
class Snapshot:
    repository: Repository
    name: str
    comment: str | None = None

    def location(self) -> str:
        return f"{self.repository.url}::{self.name}"


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


@dataclass(slots=True)
class ProgressEvent:
    total: float | None
    current: float | None
