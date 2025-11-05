import subprocess
import os
import logging
from datetime import datetime
from pathlib import Path

from tests.utilities.utilities import to_archive_path

logger = logging.getLogger(__name__)


class Borg:
    def __init__(self, borg_executable="borg"):
        """
        :param borg_executable: Path to the borg binary (default assumes it is in PATH)
        :raises RuntimeError: If borg is not found or not executable
        """
        self.borg = borg_executable

        logger.debug("Initializing Borg")

        # Verify borg exists and is executable
        self._run(["--version"])

    def list_archives(self, repository: str) -> list[str]:
        """
        List archives in a Borg repository.
        """
        logger.debug("Listing archives in repository %s", repository)

        output = self._run(["list", "--short", repository])
        return [line.strip() for line in output.splitlines() if line.strip()]

    def list_contents(self, repository: str, archive: str) -> list[Path]:
        """
        List all file and directory paths stored inside the given archive.

        Returns paths relative to the archive root (no leading slash).
        """
        logger.debug("Listing contents in archive %s::%s", repository, archive)

        if not os.path.isdir(repository):
            raise RuntimeError(f"Repository does not exist: {repository}")

        existing_archives = self.list_archives(repository)
        if archive not in existing_archives:
            raise RuntimeError(f"Archive does not exist in repository: {archive}")

        archive_ref = f"{repository}::{archive}"
        output = self._run(["list", archive_ref, "--format", "{path}\n"])

        # Path() normalizes separators (works on Linux, macOS, Windows)
        return [
            Path(line.lstrip())
            for line in output.splitlines()
            if line.strip()
        ]

    def create_repository(self, parent: Path, name: str, encryption="none") -> str:
        """
        Create a Borg repository in a new directory.

        :param parent: The parent directory to create the repository in
        :param name: The name of the repository
        :param encryption: Encryption mode (default: none)
        :return: Path to the repository
        :raises RuntimeError: If parent directory does not exist
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

        archive_name = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        archive_ref = f"{repository}::{archive_name}"

        logger.debug("Archive name is %s", archive_name)

        cmd = ["create", archive_ref] + [str(d) for d in source_dirs]

        self._run(cmd)
        return archive_name

    def restore(self, repository: str, archive: str, source_dirs: list[Path], target_dir: Path) -> None:
        """
        Restore the given directories from an archive into the target directory.

        Example:
          If the archive contains /Users/user/Documents/file.txt,
          and target_directory=/tmp/restore,
          then the file is restored to /tmp/restore/Users/user/Documents/file.txt.
        """
        # Borg expects extraction paths to be *relative* to archive root,
        # so we remove any leading slash if present.
        logger.debug("Restoring %s::%s %s into %s", repository, archive, source_dirs, target_dir)

        existing_archives = self.list_archives(repository)
        if archive not in existing_archives:
            raise RuntimeError(f"Archive does not exist in repository: {archive}")

        if not os.path.isdir(target_dir):
            raise RuntimeError(f"Target directory does not exist: {repository}")

        archive_paths = [to_archive_path(p) for p in source_dirs]

        archive_ref = f"{repository}::{archive}"

        cmd = ["extract", archive_ref] + [str(p) for p in archive_paths]
        self._run(cmd, cwd=str(target_dir))

    def _run(self, args: list[str], cwd: str | None = None) -> str:
        try:
            cmd = [self.borg] + args

            logger.debug(f"Running {cmd}")

            result = subprocess.run(
                cmd,
                cwd=cwd,
                check=True,
                text=True,
                capture_output=True
            )

            return result.stdout

        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            stderr = getattr(e, "stderr", "") or ""
            stderr = stderr.strip()
            raise RuntimeError(f"Borg failed with error: {stderr}") from e
