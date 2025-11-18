import logging
from collections.abc import Callable, Iterable
from enum import Enum
from pathlib import Path
from typing import TypeVar

from easyborg.process import ProcessError, assert_executable_valid, run_async

logger = logging.getLogger(__name__)

T = TypeVar("T")


class SortOrder(str, Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


class Fzf:
    def __init__(self, executable: Path) -> None:
        """
        Initialize an Fzf instance.
        """
        logger.debug("Initializing fzf (executable: '%s')", executable)
        assert_executable_valid(executable)
        self.executable_path = executable

    def confirm(self, prompt: str) -> bool | None:
        response = self.select_strings(["MAYBE", "NO", "YES"], prompt=prompt)
        if len(response) == 0:
            return None
        return response[0] == "YES"

    def select_items(
        self,
        items: Iterable[T],
        key: Callable[[T], str],
        *,
        multi: bool = False,
        prompt: str | None = None,
        sort_order: SortOrder | None = None,
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

        return [lookup[k] for k in selected_keys]

    def select_strings(
        self,
        items: Iterable[str],
        *,
        multi: bool = False,
        prompt: str = "Select: ",
    ) -> list[str]:
        """
        Run fzf on a stream of items and return the selected items.
        Returns [] if the user cancels.

        The items iterable is streamed directly into fzf via stdin,
        allowing very large lists without storing them in memory.
        """
        cmd = [str(self.executable_path)]
        if multi:
            cmd.append("--multi")
        cmd.append(f"--prompt={prompt}")
        cmd.append("--cycle")
        cmd.append("--color=prompt:-1,marker:bright-cyan,pointer:cyan,hl:cyan,hl+:bright-cyan")
        cmd.append("--margin=1")
        cmd.append("--info=right")
        if multi:
            # cmd.append("--marker=■ ")
            # cmd.append("--marker=▌")
            cmd.append("--marker=█ ")
        else:
            cmd.append("--marker=")

        try:
            return list(run_async(cmd, input_lines=items))
        except ProcessError as e:
            if e.return_code == 130:
                return []
            raise
