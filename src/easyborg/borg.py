import logging
import os
import subprocess
from collections.abc import Iterator
from pathlib import Path

from easyborg.util import to_relative_path, to_snapshot_ref

logger = logging.getLogger(__name__)


class Borg:
    def __init__(self, borg_executable="borg"):
        """
        Initialize a Borg instance.
        """
        logger.debug("Initializing Borg (executable: %s)", borg_executable)

        self.borg = borg_executable

        # Verify borg exists and is executable
        self._run_sync(["--version"])

    def repository_accessible(self, repository: str) -> bool:
        """
        Return True if the repository exists and is accessible.
        """
        try:
            self._run_sync(["info", repository])
            return True
        except RuntimeError:
            return False

    def snapshot_exists(self, repository: str, snapshot: str) -> bool:
        return snapshot in self.list_snapshots(repository)

    def list_snapshots(self, repository: str) -> list[str]:
        """
        List all snapshots in a Borg repository.
        """
        logger.debug("Listing snapshots in repository %s", repository)

        return self._run_sync(["list", "--short", repository])

    def list_contents(self, repository: str, snapshot: str) -> Iterator[Path]:
        """
        Yield all file and folder paths stored inside the given snapshot.

        All returned paths are relative to the snapshot root (no leading slash).
        """
        logger.debug("Listing contents of %s::%s", repository, snapshot)

        snapshot_ref = to_snapshot_ref(repository, snapshot)

        for line in self._run_async(["list", snapshot_ref, "--format", "{path}\n"]):
            if line:
                yield Path(line)

    def create_repository(self, parent: Path, name: str, encryption="none") -> str:
        """
        Create a Borg repository in a new directory.
        """
        logger.debug("Creating repository %s in %s", name, parent)

        if not parent.is_dir():
            raise RuntimeError(f"Parent directory does not exist: {parent}")

        directory = parent.joinpath(name)
        directory.mkdir(parents=False, exist_ok=False)

        self._run_sync(["init", f"--encryption={encryption}", str(directory)])

        return str(directory)

    def create_snapshot(self, repository: str, snapshot: str, folders: list[Path]):
        """
        Create a new snapshot.
        """
        snapshot_ref = to_snapshot_ref(repository, snapshot)
        logger.debug("Creating snapshot %s", snapshot_ref)

        for f in folders:
            if not os.path.isdir(f):
                raise RuntimeError(f"Folder does not exist: {f}")

        cmd = ["create", snapshot_ref, *map(str, folders)]

        self._run_sync(cmd)

    def restore(self, repository: str, snapshot: str, target_dir: Path, folders: list[Path] | None = None) -> None:
        """
        Restore folders from a snapshot into a local directory.

        If `folders` is empty or None, the entire snapshot is restored.
        """
        if folders is None:
            folders = []

        logger.debug(
            "Restoring %s -> %s -> %s into %s",
            repository,
            snapshot,
            folders,
            target_dir,
        )

        if not target_dir.is_dir():
            raise RuntimeError(f"Target directory does not exist: {target_dir}")

        relative_paths = [to_relative_path(p) for p in folders]
        snapshot_ref = to_snapshot_ref(repository, snapshot)
        cmd = ["extract", snapshot_ref, *map(str, relative_paths)]

        self._run_sync(cmd, cwd=str(target_dir))

    def _run_sync(self, args: list[str], cwd: str | None = None) -> list[str]:
        """
        Runs the borg executable synchronously.
        """
        return list(self._run_async(args, cwd=cwd))

    def _run_async(self, args: list[str], cwd: str | None = None):
        """
        Runs the borg executable asynchronously.
        """
        cmd = [self.borg] + args
        logger.debug("Running: %s", cmd)

        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        assert process.stdout is not None
        for line in process.stdout:
            yield line.rstrip("\n")

        # only after stdout is consumed do we wait for exit status
        returncode = process.wait()
        if returncode != 0:
            stderr = process.stderr.read().strip() if process.stderr else ""
            raise RuntimeError(f"Borg failed with error: {stderr}")
