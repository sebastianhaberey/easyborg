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


def run_sync(cmd: list[str], *, cwd: str | None = None, input_lines: Iterable[str] | str | None = None) -> list[str]:
    """
    Run the subprocess and return all output lines as a list.
    Raises ProcessError on failure.
    """
    return list(run_async(cmd, cwd=cwd, input_lines=input_lines))


def run_async(
    cmd: list[str],
    *,
    input_lines: Iterable[str] | None = None,
    cwd: str | None = None,
    stream: str = "stdout",  # can be "stdout" or "stderr"
) -> Iterator[str]:
    """
    Run a subprocess and yield lines from either stdout or stderr.
    """
    logger.debug("Running: %s", cmd)

    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdin=subprocess.PIPE if input_lines is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    if input_lines is not None:
        assert process.stdin is not None
        for line in input_lines:
            process.stdin.write(line + "\n")
        process.stdin.close()

    stream_pipe = process.stdout if stream == "stdout" else process.stderr
    assert stream_pipe is not None

    for line in stream_pipe:
        yield line.rstrip("\n")

    return_code = process.wait()
    if return_code != 0:
        stderr = process.stderr.read().strip() if process.stderr else None
        raise ProcessError(return_code, stderr)
