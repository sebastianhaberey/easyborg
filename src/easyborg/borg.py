import logging
import os
import subprocess
from collections.abc import Iterator
from pathlib import Path

from easyborg.util import create_archive_name, to_archive_path, to_archive_ref

logger = logging.getLogger(__name__)


class Borg:
    def __init__(self, borg_executable="borg"):
        """
        Initialize a Borg instance.

        :param borg_executable: Path to the borg binary (default assumes it is in PATH)
        :raises RuntimeError: If borg is not found or not executable
        """
        logger.debug("Initializing Borg (executable: %s)", borg_executable)

        self.borg = borg_executable

        # Verify borg exists and is executable
        self._run(["--version"])

    def list_archives(self, repository: str) -> list[str]:
        """
        List all archives in a Borg repository.
        """
        logger.debug("Listing archives in repository %s", repository)

        return self._run(["list", "--short", repository])

    def list_contents(self, repository: str, archive: str) -> Iterator[Path]:
        """
        Yield all file and directory paths stored inside the given archive.

        Paths are relative to the archive root (no leading slash).
        """
        logger.debug("Listing contents in archive %s::%s", repository, archive)

        existing_archives = self.list_archives(repository)
        if archive not in existing_archives:
            raise RuntimeError(f"Archive does not exist in repository: {archive}")

        archive_ref = to_archive_ref(repository, archive)

        for line in self._run_async(["list", archive_ref, "--format", "{path}\n"]):
            if line:
                yield Path(line)

    def create_repository(self, parent: Path, name: str, encryption="none") -> str:
        """
        Create a Borg repository in a new directory.

        :param parent: The parent directory to create the repository in (must exist)
        :param name: The name of the repository (will be the repository directory name)
        :param encryption: Encryption mode (default: none)
        :return: Path to the repository
        :raises RuntimeError: If repository could not be created
        """
        logger.debug("Creating repository %s in %s", name, parent)

        if not parent.is_dir():
            raise RuntimeError(f"Parent directory does not exist: {parent}")

        directory = parent.joinpath(name)

        directory.mkdir(parents=False, exist_ok=False)

        # Convert to string only where subprocess requires it
        self._run(["init", f"--encryption={encryption}", str(directory)])

        return str(directory)

    def archive(self, repository: str, source_dirs: list[Path]) -> str:
        """
        Create a new archive in the given repository using the provided directories.
        The archive name is timestamp-based for uniqueness.
        """
        logger.debug("Creating archive in repository %s", repository)

        for d in source_dirs:
            if not os.path.isdir(d):
                raise RuntimeError(f"Source directory does not exist: {d}")

        archive_name = create_archive_name()
        logger.debug("Archive name is %s", archive_name)

        archive_ref = to_archive_ref(repository, archive_name)

        cmd = ["create", archive_ref, *map(str, source_dirs)]

        self._run(cmd)
        return archive_name

    def restore(
        self, repository: str, archive: str, source_dirs: list[Path], target_dir: Path
    ) -> None:
        """
        Restore the given directories from an archive into the target directory.

        Example:
          If the archive contains /Users/user/Documents/file.txt,
          and target_directory=/tmp/restore,
          then the file is restored to /tmp/restore/Users/user/Documents/file.txt.
        """
        logger.debug(
            "Restoring %s -> %s -> %s into %s",
            repository,
            archive,
            source_dirs,
            target_dir,
        )

        existing_archives = self.list_archives(repository)
        if archive not in existing_archives:
            raise RuntimeError(f"Archive does not exist in repository: {archive}")

        if not target_dir.is_dir():
            raise RuntimeError(f"Target directory does not exist: {target_dir}")

        # Borg expects extraction paths to be *relative* to archive root,
        # so we remove any leading slash if present.
        archive_paths = [to_archive_path(p) for p in source_dirs]

        archive_ref = to_archive_ref(repository, archive)

        cmd = ["extract", archive_ref] + [str(p) for p in archive_paths]
        self._run(cmd, cwd=str(target_dir))

    def _run(self, args: list[str], cwd: str | None = None) -> list[str]:
        return [line for line in self._run_async(args, cwd=cwd)]

    def _run_async(self, args: list[str], cwd: str | None = None):
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
