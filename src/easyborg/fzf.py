import logging
from collections.abc import Callable, Iterable
from enum import Enum
from pathlib import Path
from typing import TypeVar

from easyborg.process import ProcessError, assert_executable_valid, run_async
from easyborg.theme import StyleId, SymbolId, ThemeType, theme

STYLES = theme().styles_fzf
SYMBOLS = theme().symbols

logger = logging.getLogger(__name__)

T = TypeVar("T")

DEFAULT_COLORS = {
    "prompt": STYLES[StyleId.PRIMARY],
    "marker": STYLES[StyleId.PRIMARY],
    "pointer": STYLES[StyleId.PRIMARY],
    "hl": STYLES[StyleId.PRIMARY],
    "hl+": STYLES[StyleId.PRIMARY],
    "spinner": STYLES[StyleId.PRIMARY],
    "info": "-1:regular",
    "input-fg": "-1:regular",
}

DANGER_COLORS = {
    "prompt": STYLES[StyleId.DANGER],
    "marker": STYLES[StyleId.DANGER],
    "pointer": STYLES[StyleId.DANGER],
    "hl": STYLES[StyleId.DANGER],
    "hl+": STYLES[StyleId.DANGER],
}


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

    def select_items(
        self,
        items: Iterable[T],
        key: Callable[[T], str],
        *,
        multi: bool = False,
        sort_order: SortOrder | None = None,
        show_info: bool = False,
        danger: bool = False,
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

        selected_keys = self.select_strings(keys, multi=multi, show_info=show_info, danger=danger)

        return [lookup[k] for k in selected_keys]

    def select_strings(
        self,
        items: Iterable[str],
        *,
        multi: bool = False,
        show_info: bool = False,
        danger: bool = False,
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
        cmd.append(f"--prompt={SYMBOLS[SymbolId.PROMPT]}")
        cmd.append(f"--pointer={SYMBOLS[SymbolId.POINTER]}")
        cmd.append("--gutter= ")
        cmd.append("--height=~90%")  # grow according to content, but max. 90% of terminal height
        cmd.append("--cycle")
        cmd.append(f"--color={_colors(theme().type, danger)}")
        cmd.append("--margin=0,0,0,0")
        cmd.append("--info=right")
        cmd.append("--no-separator")
        cmd.append("--reverse")
        cmd.append("--no-mouse")
        if show_info:
            cmd.append("--info=inline-right")
        else:
            cmd.append("--no-info")
        if multi:
            cmd.append(f"--marker={SYMBOLS[SymbolId.MARKER]}")
        else:
            cmd.append("--marker=")

        try:
            return list(run_async(cmd, input_lines=items))
        except ProcessError as e:
            if e.return_code == 130:
                return []
            raise


def _colors(theme_type: ThemeType, danger: bool) -> str:
    mode = "light" if theme_type == ThemeType.LIGHT else "dark"
    colors = DEFAULT_COLORS
    if danger:
        colors |= DANGER_COLORS

    return f"{mode}," + ",".join(f"{k}:{v}" for k, v in colors.items())
