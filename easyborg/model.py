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


@dataclass(frozen=True, slots=True)
class Repository:
    name: str
    url: str
    type: RepositoryType


@dataclass(frozen=True, slots=True)
class Config:
    source: Path
    backup_folders: list[Path]
    repos: dict[str, Repository]
    compact_probability: float = 0.10  # TODO SH is this the right place for defaults?


@dataclass(frozen=True, slots=True)
class Context:
    profile: str
    log_dir: Path
    log_file: Path
    log_level: str
    config_dir: Path
    config_file: Path
    test: bool
    tty: bool
    expert: bool


@dataclass(frozen=True, slots=True)
class ProgressEvent:
    total: float | None = None
    current: float | None = None
    message: str | None = None
