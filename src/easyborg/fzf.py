import logging
import subprocess
from collections.abc import Iterable

logger = logging.getLogger(__name__)


class Fzf:
    def __init__(self, fzf_executable: str = "fzf"):
        """
        Initialize an Fzf instance.

        :param fzf_executable: Path to the fzf binary (default assumes it is in PATH)
        :raises RuntimeError: If fzf is not found or not executable
        """
        self.fzf = fzf_executable
        self._verify()

    def select_one(self, items: Iterable[str], prompt: str | None = None) -> str | None:
        """
        Let the user choose *one* value via fzf.
        Returns the selected string or None if cancelled.
        """
        selections = self._run(multi=False, items=items, prompt=prompt)
        return selections[0] if selections else None

    def select_many(self, items: Iterable[str], prompt: str | None = None) -> list[str]:
        """
        Let the user choose *multiple* values via fzf (--multi).
        Returns list of selected strings (may be empty).
        """
        return self._run(multi=True, items=items, prompt=prompt)

    def _verify(self):
        try:
            subprocess.run([self.fzf, "--version"], check=True, capture_output=True, text=True)
        except Exception as e:
            raise RuntimeError(f"Could not execute fzf: {self.fzf}") from e

    def _run(self, *, multi: bool, items: Iterable[str], prompt: str | None) -> list[str]:
        """
        Feed lines into fzf and return the selected ones.
        """
        cmd = [self.fzf]
        if multi:
            cmd.append("--multi")
        if prompt:
            cmd.append(f"--prompt={prompt}")

        logger.debug("Running: %s", cmd)

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        assert process.stdin is not None
        for item in items:
            process.stdin.write(item + "\n")
        process.stdin.close()

        assert process.stdout is not None
        selections = [line.rstrip("\n") for line in process.stdout]

        returncode = process.wait()
        if returncode != 0:
            return []  # User cancelled or no selection

        return selections
