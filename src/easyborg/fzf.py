import logging
from collections.abc import Callable, Iterable
from typing import TypeVar

from easyborg.process import ProcessError, assert_executable, run_async

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Fzf:
    def __init__(self, fzf_executable: str = "fzf"):
        """
        Initialize an Fzf instance.
        """
        assert_executable(fzf_executable)
        self.fzf = fzf_executable

    def select_item(
        self,
        items: Iterable[T],
        *,
        key: Callable[[T], str],
        multi: bool = False,
        prompt: str,
    ) -> list[T]:
        """
        Select objects using fzf based on a string key function.
        """
        # Build lookup table (preserves unique mapping)
        lookup = {key(item): item for item in items}

        # Stream just the keys to fzf
        selected_keys = self.select(lookup.keys(), multi=multi, prompt=prompt)

        # Map strings back to original objects
        return [lookup[k] for k in selected_keys]

    def select(
        self,
        items: Iterable[str],
        *,
        multi: bool = False,
        prompt: str,
    ) -> list[str]:
        """
        Run fzf on a stream of items and return the selected items.
        Returns [] if the user cancels.

        The items iterable is streamed directly into fzf via stdin,
        allowing very large lists without storing them in memory.
        """
        cmd = [self.fzf]
        if multi:
            cmd.append("--multi")
        cmd.append(f"--prompt={prompt}")

        try:
            return list(run_async(cmd, input=items))
        except ProcessError as e:
            if e.return_code == 130:
                return []
            raise
