from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from functools import cached_property

from cloup import Style as CloupStyle
from rich.style import Style as RichStyle


class StyleId(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    HEADER = "header"
    DANGER = "danger"
    GRAY = "gray"


class SymbolId(Enum):
    PROMPT = "prompt"
    POINTER = "pointer"
    MARKER = "marker"
    DANGER = "danger"


class ThemeType(Enum):
    DARK = "dark"
    LIGHT = "light"


_RICH_TO_FZF_COLORS = {
    # normal
    "black": "black",
    "red": "red",
    "green": "green",
    "yellow": "yellow",
    "blue": "blue",
    "magenta": "magenta",
    "cyan": "cyan",
    "white": "white",
    # bright
    "bright_black": "bright-black",
    "bright_red": "bright-red",
    "bright_green": "bright-green",
    "bright_yellow": "bright-yellow",
    "bright_blue": "bright-blue",
    "bright_magenta": "bright-magenta",
    "bright_cyan": "bright-cyan",
    "bright_white": "bright-white",
}


def rich_to_fzf(style: RichStyle) -> str:
    """Convert a Rich style to an fzf style string."""
    parts: list[str] = []

    if style.color:
        name = style.color.name
        if name in _RICH_TO_FZF_COLORS:
            parts.append(_RICH_TO_FZF_COLORS[name])

    if style.bold:
        parts.append("bold")
    if style.italic:
        parts.append("italic")
    if style.underline:
        parts.append("underline")
    if style.strike:
        parts.append("strikethrough")
    if style.dim:
        parts.append("dim")
    if style.reverse:
        parts.append("reverse")

    return ":".join(parts)


def rich_to_cloup(style: RichStyle) -> CloupStyle:
    """Convert a Rich style to a Cloup (Click-compatible) style."""
    kwargs = {}

    if style.color:
        name = style.color.name
        if name.startswith("bright_"):
            kwargs["fg"] = "bright-" + name.split("_", 1)[1]
        else:
            kwargs["fg"] = name

    kwargs["bold"] = bool(style.bold)
    # kwargs["dim"] = bool(style.dim)
    kwargs["italic"] = bool(style.italic)
    kwargs["underline"] = bool(style.underline)
    kwargs["strikethrough"] = bool(style.strike)
    kwargs["reverse"] = bool(style.reverse)

    return CloupStyle(**kwargs)


@dataclass(frozen=True)
class Theme:
    """Rich-based theme, with automatic export to cloup and fzf formats."""

    type: ThemeType
    styles: dict[StyleId, RichStyle]
    symbols: dict[SymbolId, str]

    @staticmethod
    def melody_dark() -> Theme:
        return Theme(
            type=ThemeType.DARK,
            styles={
                StyleId.PRIMARY: RichStyle(color="cyan", bold=True),
                StyleId.SECONDARY: RichStyle(color="magenta", bold=True),
                StyleId.SUCCESS: RichStyle(color="green", bold=True),
                StyleId.WARNING: RichStyle(color="yellow", bold=True),
                StyleId.ERROR: RichStyle(color="red", bold=True),
                StyleId.DANGER: RichStyle(color="red", bold=True),
                StyleId.HEADER: RichStyle(color="yellow", bold=True),
                StyleId.GRAY: RichStyle(color="black", bold=True),
            },
            symbols={
                SymbolId.PROMPT: "➜ ",
                SymbolId.POINTER: "▏",
                SymbolId.MARKER: "✔ ",
                SymbolId.DANGER: "DANGER ",
            },
        )

    @staticmethod
    def melody_light() -> Theme:
        dark = Theme.melody_dark()
        return Theme(
            type=ThemeType.LIGHT,
            styles=dark.styles | {StyleId.GRAY: RichStyle(color="white", bold=False)},
            symbols=dark.symbols,
        )

    @staticmethod
    def ice_dark() -> Theme:
        return Theme(
            type=ThemeType.DARK,
            styles={
                StyleId.PRIMARY: RichStyle(color="cyan", bold=True),
                StyleId.SECONDARY: RichStyle(color="cyan", bold=False),
                StyleId.SUCCESS: RichStyle(color="green", bold=True),
                StyleId.WARNING: RichStyle(color="yellow", bold=True),
                StyleId.ERROR: RichStyle(color="red", bold=True),
                StyleId.DANGER: RichStyle(color="red", bold=True),
                StyleId.HEADER: RichStyle(color="white", bold=True),
                StyleId.GRAY: RichStyle(color="black", bold=True),
            },
            symbols={
                SymbolId.PROMPT: "➜ ",
                SymbolId.POINTER: "▌",
                SymbolId.MARKER: "➜ ",
                SymbolId.DANGER: "DANGER ",
            },
        )

    @staticmethod
    def ice_light() -> Theme:
        dark = Theme.ice_dark()
        return Theme(
            type=ThemeType.LIGHT,
            styles=dark.styles | {StyleId.GRAY: RichStyle(color="white", bold=False)},
            symbols=dark.symbols,
        )

    @staticmethod
    def from_name(name: str) -> Theme:
        name = name.lower().strip()
        if name == "melody_dark":
            return Theme.melody_dark()
        if name == "melody_light":
            return Theme.melody_light()
        if name == "ice_dark":
            return Theme.ice_dark()
        if name == "ice_light":
            return Theme.ice_light()
        raise ValueError(f"Unknown theme: {name}")

    # --- Lazy conversion properties ---------------------------------------------

    @cached_property
    def styles_cloup(self) -> dict[StyleId, CloupStyle]:
        return {sid: rich_to_cloup(style) for sid, style in self.styles.items()}

    @cached_property
    def styles_fzf(self) -> dict[StyleId, str]:
        return {sid: rich_to_fzf(style) for sid, style in self.styles.items()}


def _initialize_theme() -> Theme:
    return Theme.from_name(os.getenv("EASYBORG_THEME", "melody_dark"))


_THEME = _initialize_theme()


def theme() -> Theme:
    """Get the global Theme instance."""
    if _THEME is None:
        raise RuntimeError("Theme not initialized")
    return _THEME
