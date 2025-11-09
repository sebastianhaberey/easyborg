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

    def select_one_item(
        self,
        items: Iterable[T],
        *,
        key: Callable[[T], str],
        prompt: str,
        sortOrder: SortOrder = None,
    ) -> T:
        selected = self._select_items(items, key=key, multi=False, prompt=prompt, sortOrder=sortOrder)
        return selected[0] if selected else None

    def select_multiple_items(
        self,
        items: Iterable[T],
        *,
        key: Callable[[T], str],
        prompt: str,
        sortOrder: SortOrder = None,
    ) -> T:
        return self._select_items(items, key=key, multi=True, prompt=prompt, sortOrder=sortOrder)

    def select_one_string(
        self,
        items: Iterable[str],
        *,
        prompt: str,
        sortOrder: SortOrder = None,
    ) -> str:
        selected = self._select(items, multi=False, prompt=prompt)
        return selected[0] if selected else None

    def select_multiple_strings(
        self,
        items: Iterable[str],
        *,
        prompt: str,
    ) -> list[str]:
        return self._select(items, multi=True, prompt=prompt)

    def _select_items(
        self,
        items: Iterable[T],
        *,
        key: Callable[[T], str],
        multi: bool = False,
        prompt: str,
        sortOrder: SortOrder = None,
    ) -> list[T]:
        """
        Select objects using fzf based on a string key function.
        """
        lookup = {key(item): item for item in items}
        keys = list(lookup.keys())

        if sortOrder is not None:
            keys.sort(reverse=True if sortOrder == SortOrder.DESCENDING else False)

        selected_keys = self._select(keys, multi=multi, prompt=prompt)

        return [lookup[k] for k in selected_keys]

    def _select(
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
