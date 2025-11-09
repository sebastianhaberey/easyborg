import logging
import os
from collections.abc import Iterator
from pathlib import Path

from easyborg.model import Repository, RepositoryType, Snapshot
from easyborg.process import assert_executable, run_async, run_sync
from easyborg.util import to_relative_path

logger = logging.getLogger(__name__)


class Borg:
    def __init__(self, borg_executable="borg"):
        """
        Initialize a Borg instance.
        """
        logger.debug("Initializing Borg (executable: %s)", borg_executable)

        assert_executable(borg_executable)
        self.borg = borg_executable

    def repository_accessible(self, repo: Repository) -> bool:
        """
        Return True if the repository exists and is accessible.
        """
        try:
            run_sync([self.borg, "info", repo.url])
            return True
        except RuntimeError:
            return False

    def snapshot_exists(self, snap: Snapshot) -> bool:
        """
        Return True if the snapshot exists.
        """
        return snap.name in (s.name for s in self.list_snapshots(snap.repo))

    def list_snapshots(self, repo: Repository) -> list[Snapshot]:
        """
        List all snapshots in the given repository.
        """
        logger.debug("Listing snapshots in %s (%s)", repo.name, repo.url)

        lines = run_sync([self.borg, "list", repo.url, "--format", "{archive}{TAB}{comment}\n"])

        snapshots = []
        for line in lines:
            name, _, comment = line.partition("\t")
            snapshots.append(Snapshot(repo, name, comment if comment else None))

        return snapshots

    def list_contents(self, snap: Snapshot) -> Iterator[Path]:
        """
        Yield all files and folders contained in a snapshot.
        Paths are always relative (no leading slash).
        """
        logger.debug("Listing contents of %s", snap.location())

        for line in run_async([self.borg, "list", snap.location(), "--format", "{path}\n"]):
            if line:
                yield Path(line)

    def create_repository(self, parent: Path, name: str, *, encryption="none", dry_run: bool = False) -> Repository:
        """
        Create a Borg repository.
        """
        logger.debug("Creating repository %s in %s", name, parent)

        if not parent.is_dir():
            raise RuntimeError(f"Parent directory does not exist: {parent}")

        directory = parent / name
        directory.mkdir(parents=False, exist_ok=False)

        cmd = [self.borg, "init"]
        if dry_run:
            cmd.append("--dry-run")
        cmd.extend([f"--encryption={encryption}", str(directory)])

        run_sync(cmd)

        return Repository(name=name, url=str(directory), type=RepositoryType.BACKUP)

    def create_snapshot(self, snap: Snapshot, folders: list[Path], *, dry_run: bool = False):
        """
        Create a new snapshot.
        """
        logger.debug("Creating snapshot %s", snap.location())

        for folder in folders:
            if not os.path.isdir(folder):
                raise RuntimeError(f"Folder does not exist: {folder}")

        cmd = [self.borg, "create"]
        if dry_run:
            cmd.append("--dry-run")
        if snap.comment:
            cmd.extend(["--comment", snap.comment])
        cmd.extend([snap.location(), *map(str, folders)])

        run_sync(cmd)

    def restore(self, snap: Snapshot, target_dir: Path, folders: list[Path] | None = None, *, dry_run: bool = False):
        """
        Restore folders (or the entire snapshot if folders=None) into target_dir.
        """
        if folders is None:
            folders = []

        logger.debug("Restoring %s -> %s", snap.location(), target_dir)

        if not target_dir.is_dir():
            raise RuntimeError(f"Target directory does not exist: {target_dir}")

        # make absolute folders relative for safety
        relative_folders = [to_relative_path(folder) for folder in folders]

        cmd = [self.borg, "extract"]
        if dry_run:
            cmd.append("--dry-run")
        cmd.extend([snap.location(), *map(str, relative_folders)])

        run_sync(cmd, cwd=str(target_dir))

    def prune(self, repo: Repository, *, dry_run: bool = False) -> None:
        """
        Prune old snapshots in the repository according to retention policy.
        """
        logger.debug("Pruning snapshots in %s (%s)", repo.name, repo.url)

        cmd = [
            self.borg,
            "prune",
            repo.url,
            "--keep-daily=7",
            "--keep-weekly=12",
            "--keep-monthly=12",
        ]

        if dry_run:
            cmd.append("--dry-run")

        run_sync(cmd)

    def compact(self, repo: Repository, *, dry_run: bool = False) -> None:
        """
        Run `borg compact` to reclaim space.
        """
        logger.debug("Compacting repository %s (%s)", repo.name, repo.url)

        cmd = [self.borg, "compact", repo.url]

        if dry_run:
            cmd.append("--dry-run")

        run_sync(cmd)
