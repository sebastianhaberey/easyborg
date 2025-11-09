import logging
from collections.abc import Callable, Iterable
from enum import Enum
from typing import TypeVar

from easyborg.process import ProcessError, assert_executable, run_async

logger = logging.getLogger(__name__)

T = TypeVar("T")


class SortOrder(str, Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


class Fzf:
    def __init__(self, fzf_executable: str = "fzf"):
        """
        Initialize an Fzf instance.
        """
        assert_executable(fzf_executable)
        self.fzf = fzf_executable

    def select_items(
        self,
        items: Iterable[T],
        *,
        key: Callable[[T], str],
        multi: bool = False,
        prompt: str,
        sort_order: SortOrder = None,
    ) -> list[T]:
        """
        Select objects using fzf based on a string key function.
        """
        lookup = {}
        for item in items:
            k = key(item)
            if k in lookup:
                raise ValueError(f"Duplicate key detected: {k!r}")
            lookup[k] = item

        keys = list(lookup.keys())

        if sort_order is not None:
            keys.sort(reverse=True if sort_order == SortOrder.DESCENDING else False)

        selected_keys = self.select_strings(keys, multi=multi, prompt=prompt)

        for item in items:
            k = key(item)
            if k in lookup:
                raise ValueError(f"Duplicate fzf key detected: {k!r}")
            lookup[k] = item

        return [lookup[k] for k in selected_keys]

    def select_strings(
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
            return list(run_async(cmd, input_lines=items))
        except ProcessError as e:
            if e.return_code == 130:
                return []
            raise
