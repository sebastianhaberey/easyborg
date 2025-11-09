# easyborg/util/run.py

import logging
import subprocess
from collections.abc import Iterable, Iterator

logger = logging.getLogger(__name__)


class ProcessError(RuntimeError):
    def __init__(self, return_code: int, stderr: str | None = None):
        self.return_code = return_code
        self.stderr = stderr
        msg = f"Process failed with exit code {return_code}"
        if stderr:
            msg += f": {stderr}"
        super().__init__(msg)


def assert_executable(executable: str):
    """
    Ensure binary is installed and callable.
    """
    cmd = [executable, "--version"]
    try:
        run_sync(cmd)
    except ProcessError as e:
        raise RuntimeError(f"Could not execute {cmd}") from e


def run_sync(cmd: list[str], cwd: str | None = None) -> list[str]:
    """
    Run the subprocess and return all output lines as a list.
    Raises ProcessError on failure.
    """
    return list(run_async(cmd, cwd=cwd))


def run_async(
    cmd: list[str],
    *,
    input: Iterable[str] | None = None,
    cwd: str | None = None,
) -> Iterator[str]:
    """
    Run a subprocess and yield stdout lines as they arrive.
    Raises ProcessError(return_code) on non-zero exit.
    """
    logger.debug("Running: %s", cmd)

    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdin=subprocess.PIPE if input is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Feed streaming input to stdin
    if input is not None:
        assert process.stdin is not None
        for line in input:
            process.stdin.write(line + "\n")
        process.stdin.close()

    assert process.stdout is not None
    for line in process.stdout:
        yield line.rstrip("\n")

    return_code = process.wait()

    if return_code != 0:
        stderr = process.stderr.read().strip() if process.stderr else None
        raise ProcessError(return_code, stderr)
