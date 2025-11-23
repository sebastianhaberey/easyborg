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
    def __init__(self, executable: Path, *, light_mode: bool = False) -> None:
        """
        Initialize an Fzf instance.
        """
        self.light_mode = light_mode
        logger.debug("Initializing fzf (executable: '%s')", executable)
        assert_executable_valid(executable)
        self.executable_path = executable

    def confirm(self) -> bool | None:
        response = self.select_strings(["MAYBE", "NO", "YES"])
        if len(response) == 0:
            return None
        return response[0] == "YES"

    def select_items(
        self,
        items: Iterable[T],
        key: Callable[[T], str],
        *,
        multi: bool = False,
        sort_order: SortOrder | None = None,
        show_info: bool = False,
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

        selected_keys = self.select_strings(keys, multi=multi, show_info=show_info)

        return [lookup[k] for k in selected_keys]

    def select_strings(
        self,
        items: Iterable[str],
        *,
        multi: bool = False,
        show_info: bool = False,
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
        cmd.append("--prompt=➜ ")
        cmd.append("--height=~90%")  # grow according to content, but max. 90% of terminal height
        cmd.append("--cycle")
        cmd.append(f"--color={_get_colors(self.light_mode)}")
        cmd.append("--margin=0,0,0,0")
        cmd.append("--info=right")
        cmd.append("--no-separator")
        if show_info:
            cmd.append("--info=inline-right")
        else:
            cmd.append("--no-info")
        if multi:
            cmd.append("--marker=█ ")
        else:
            cmd.append("--marker=")

        try:
            return list(run_async(cmd, input_lines=items))
        except ProcessError as e:
            if e.return_code == 130:
                return []
            raise


def _get_colors(light_mode: bool = False) -> str:
    return _get_light_colors() if light_mode else _get_dark_colors()


def _get_light_colors() -> str:
    return _color_options(
        "light",
        options={
            "prompt": "-1",
            "marker": "cyan",
            "pointer": "cyan",
            "hl": "cyan",
            "hl+": "cyan",
            "spinner": "cyan",
            "info": "-1",
        },
    )


def _get_dark_colors() -> str:
    return _color_options(
        "dark",
        options={
            "prompt": "cyan:regular",
            "marker": "bright-cyan",
            "pointer": "cyan",
            "hl": "cyan",
            "hl+": "bright-cyan",
            "spinner": "bright-cyan",
            "info": "-1:bold",
        },
    )


def _color_options(mode: str, *, options: dict[str, str] = ()) -> str:
    out = f"{mode}"
    if options:
        items = ",".join(f"{k}:{v}" for k, v in options.items())
        out += f",{items}"
    return out
