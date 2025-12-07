from __future__ import annotations

from collections.abc import Mapping
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

    def full_name(self) -> str:
        if self.comment:
            return f"{self.name} - {self.comment}"
        else:
            return f"{self.name}"


@dataclass(frozen=True, slots=True)
class Repository:
    name: str
    url: str
    type: RepositoryType
    compact_probability: float = 0.1  # TODO SH find a better place for defaults
    env: Mapping[str, str] | None = None


@dataclass(frozen=True, slots=True)
class Config:
    backup_paths: list[Path]
    repos: Mapping[str, Repository]
    env: Mapping[str, str] | None = None


@dataclass(slots=True)
class Context:
    profile: str
    log_dir: Path
    log_file: Path
    debug: bool
    headless: bool
    config_dir: Path
    config_file: Path
    test: bool
    tty: bool
    expert: bool
    easyborg_executable: Path
    borg_executable: Path
    fzf_executable: Path
    python_executable: Path
    real_python_executable: Path


@dataclass(frozen=True, slots=True)
class ProgressEvent:
    total: float | None = None
    current: float | None = None
    message: str | None = None
