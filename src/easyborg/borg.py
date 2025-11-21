import logging
import os
from collections.abc import Iterator
from pathlib import Path

from easyborg.model import ProgressEvent, Repository, RepositoryType, Snapshot
from easyborg.process import Output, assert_executable_valid, run_async, run_sync
from easyborg.progress_parser import parse_progress

logger = logging.getLogger(__name__)

# Options and arguments are written in the order recommended by Borg: borg <command> [options] [arguments].
# (see https://borgbackup.readthedocs.io/en/stable/usage/general.html#positional-arguments-and-options-order-matters)


class Borg:
    def __init__(self, executable: Path):
        """
        Initialize a Borg instance.
        """
        logger.debug("Initializing Borg (executable: '%s')", executable)
        assert_executable_valid(executable)
        self.executable = executable

    def repository_accessible(self, repo: Repository) -> bool:
        """
        Return True if the repository exists and is accessible.
        """
        try:
            cmd = [str(self.executable), "info"]
            cmd.append(repo.url)

            run_sync(cmd, env=repo.env)
            return True
        except RuntimeError:
            return False

    def snapshot_exists(self, snap: Snapshot) -> bool:
        """
        Return True if the snapshot exists.
        """
        return snap.name in (s.name for s in self.list_snapshots(snap.repository))

    def list_snapshots(self, repo: Repository) -> list[Snapshot]:
        """
        List all snapshots in the given repository.
        """
        logger.debug("Listing snapshots in repository '%s'", repo.url)

        cmd = [str(self.executable), "list"]
        cmd.extend(["--format", "{archive}{TAB}{comment}\n"])
        cmd.append(repo.url)

        lines = run_sync(cmd, env=repo.env)

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

        cmd = [str(self.executable), "list"]
        cmd.extend(["--format", "{path}\n"])
        cmd.append(snap.location())

        for line in run_async(cmd, env=snap.repository.env):
            if line:
                yield Path(line)

    def create_repository(
        self, parent: Path, name: str, type: RepositoryType, *, encryption="none", dry_run: bool = False
    ) -> Repository:
        """
        Create a Borg repository.
        """
        logger.debug("Creating repository '%s' in '%s'", name, parent)

        if not parent.is_dir():
            raise RuntimeError(f"Parent directory does not exist: {parent}")

        directory = parent / name
        directory.mkdir(parents=False, exist_ok=False)

        cmd = [str(self.executable), "init"]
        if dry_run:
            cmd.append("--dry-run")
        cmd.append(f"--encryption={encryption}")
        cmd.append(str(directory))

        run_sync(cmd)

        return Repository(name=name, url=str(directory), type=type, compact_probability=0.1, env={})

    def create_snapshot(
        self,
        snap: Snapshot,
        folders: list[Path],
        *,
        dry_run: bool = False,
        progress: bool = False,
    ):
        """
        Create a new snapshot.
        """
        logger.debug("Creating snapshot %s", snap.location())

        for folder in folders:
            if not os.path.isdir(folder):
                raise RuntimeError(f"Folder does not exist: {folder}")

        cmd = [str(self.executable), "create"]
        if progress:
            cmd.extend(["--progress", "--log-json"])
        if dry_run:
            cmd.append("--dry-run")
        if snap.comment:
            cmd.extend(["--comment", snap.comment])
        cmd.append(snap.location())
        cmd.extend(map(str, folders))

        if progress:
            return parse_progress(run_async(cmd, output=Output.STDERR, env=snap.repository.env))

        run_sync(cmd, env=snap.repository.env)
        return None

    def restore(
        self,
        snap: Snapshot,
        target_dir: Path,
        folders: list[Path] | None = None,
        *,
        dry_run: bool = False,
        progress: bool = False,
    ) -> Iterator[ProgressEvent] | None:
        """
        Restore folders (or the entire snapshot if folders=None) into target_dir.
        Returns progress events if progress=True (slows down performance).
        """
        if folders is None:
            folders = []

        logger.debug("Restoring %s into %s", snap.location(), target_dir)

        if not target_dir.is_dir():
            raise RuntimeError(f"Target directory does not exist: {target_dir}")

        cmd = [str(self.executable), "extract"]
        if progress:
            cmd.extend(["--progress", "--log-json"])
        if dry_run:
            cmd.append("--dry-run")
        cmd.extend(["--noflags", "--noacls", "--noxattrs"])  # strip OS-specific flags
        cmd.extend([snap.location(), *map(str, folders)])

        if progress:
            return parse_progress(run_async(cmd, cwd=str(target_dir), output=Output.STDERR))

        run_sync(cmd, cwd=str(target_dir), env=snap.repository.env)
        return None

    def prune(
        self,
        repo: Repository,
        *,
        dry_run: bool = False,
        progress: bool = False,
    ) -> Iterator[ProgressEvent] | None:
        """
        Prune old snapshots in the repository according to retention policy.
        """
        logger.debug("Pruning repository '%s'", repo.url)

        cmd = [str(self.executable), "prune"]
        if progress:
            cmd.extend(["--progress", "--log-json"])
        if dry_run:
            cmd.append("--dry-run")
        cmd.extend(["--keep-daily=7", "--keep-weekly=13"])
        cmd.append(repo.url)

        if progress:
            return parse_progress(run_async(cmd, output=Output.STDERR, env=repo.env))

        run_sync(cmd, env=repo.env)
        return None

    def compact(
        self,
        repo: Repository,
        *,
        dry_run: bool = False,
        progress: bool = False,
    ) -> Iterator[ProgressEvent] | None:
        """
        Run `borg compact` to reclaim space.
        """
        logger.debug("Compacting repository '%s'", repo.url)

        cmd = [str(self.executable), "compact"]
        if progress:
            cmd.extend(["--progress", "--log-json"])
        if dry_run:
            cmd.append("--dry-run")
        cmd.append(repo.url)

        if progress:
            return parse_progress(run_async(cmd, output=Output.STDERR, env=repo.env))

        run_sync(cmd, env=repo.env)
        return None

    def delete(
        self,
        snap: Snapshot,
        *,
        dry_run: bool = False,
        progress: bool = False,
    ) -> Iterator[ProgressEvent] | None:
        """
        Delete snapshot from repository.
        """
        logger.debug("Deleting snapshot '%s' from repository '%s' ", snap.name, snap.repository.url)

        cmd = [str(self.executable), "delete"]
        if progress:
            cmd.extend(["--progress", "--log-json"])
        if dry_run:
            cmd.append("--dry-run")
        cmd.append(snap.location())

        if progress:
            return parse_progress(run_async(cmd, output=Output.STDERR, env=snap.repository.env))

        run_sync(cmd, env=snap.repository.env)
        return None
