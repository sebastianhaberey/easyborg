# easyborg/theme.py
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

VALID_COLORS = set(_RICH_TO_FZF_COLORS.keys())

VALID_ATTRS = {
    "bold",
    "italic",
    "underline",
    "reverse",
    "dim",
    "strikethrough",
}


def parse_style_string(s: str):
    """
    Parse a style string like "cyan bold underline" into (color_name, attributes_set)
    """
    parts = s.lower().split()
    color = None
    attrs = set()

    for p in parts:
        if p in VALID_COLORS:
            color = p
        elif p in VALID_ATTRS:
            attrs.add(p)
        else:
            raise ValueError(f"Unknown style token: {p}")

    return color, attrs


def string_to_rich(s: str) -> RichStyle:
    color, attrs = parse_style_string(s)
    return RichStyle(
        color=color,
        bold="bold" in attrs,
        italic="italic" in attrs,
        underline="underline" in attrs,
        dim="dim" in attrs,
        reverse="reverse" in attrs,
        strike="strikethrough" in attrs,
    )


def string_to_cloup(s: str) -> CloupStyle:
    color, attrs = parse_style_string(s)

    kwargs = {}

    if color:
        if color.startswith("bright_"):
            kwargs["fg"] = "bright-" + color.split("_", 1)[1]
        else:
            kwargs["fg"] = color

    kwargs["bold"] = "bold" in attrs
    kwargs["italic"] = "italic" in attrs
    kwargs["underline"] = "underline" in attrs
    kwargs["strikethrough"] = "strikethrough" in attrs
    kwargs["reverse"] = "reverse" in attrs
    # Click/Cloup does not support "dim"

    return CloupStyle(**kwargs)


def string_to_fzf(s: str) -> str:
    color, attrs = parse_style_string(s)
    parts = []

    if color:
        parts.append(_RICH_TO_FZF_COLORS[color])

    for a in attrs:
        if a == "strikethrough":
            parts.append("strikethrough")
        else:
            parts.append(a)

    return ":".join(parts)


@dataclass(frozen=True)
class Theme:
    type: ThemeType
    styles: dict[StyleId, str]
    symbols: dict[SymbolId, str]

    @staticmethod
    def melody_dark() -> Theme:
        return Theme(
            type=ThemeType.DARK,
            styles={
                StyleId.PRIMARY: "cyan bold",
                StyleId.SECONDARY: "magenta bold",
                StyleId.SUCCESS: "green bold",
                StyleId.WARNING: "yellow bold",
                StyleId.ERROR: "red bold",
                StyleId.DANGER: "red bold",
                StyleId.HEADER: "yellow bold",
                StyleId.GRAY: "black bold",
            },
            symbols={
                SymbolId.PROMPT: "➜ ",
                SymbolId.POINTER: "▌",
                SymbolId.MARKER: "✔ ",
                SymbolId.DANGER: "DANGER ",
            },
        )

    @staticmethod
    def melody_light() -> Theme:
        dark = Theme.melody_dark()
        return Theme(
            type=ThemeType.LIGHT,
            styles=dark.styles | {StyleId.GRAY: "white"},
            symbols=dark.symbols,
        )

    @staticmethod
    def ice_dark() -> Theme:
        return Theme(
            type=ThemeType.DARK,
            styles={
                StyleId.PRIMARY: "blue bold",
                StyleId.SECONDARY: "cyan bold",
                StyleId.SUCCESS: "green bold",
                StyleId.WARNING: "yellow bold",
                StyleId.ERROR: "red bold",
                StyleId.DANGER: "red bold",
                StyleId.HEADER: "white bold",
                StyleId.GRAY: "black bold",
            },
            symbols={
                SymbolId.PROMPT: "➜ ",
                SymbolId.POINTER: "▌",
                SymbolId.MARKER: "✔ ",
                SymbolId.DANGER: "DANGER ",
            },
        )

    @staticmethod
    def ice_light() -> Theme:
        dark = Theme.ice_dark()
        return Theme(
            type=ThemeType.LIGHT,
            styles=dark.styles | {StyleId.GRAY: "white"},
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

    # ------------------------------------------------------------------
    # Lazy conversions
    # ------------------------------------------------------------------

    @cached_property
    def styles_rich(self) -> dict[StyleId, RichStyle]:
        return {sid: string_to_rich(s) for sid, s in self.styles.items()}

    @cached_property
    def styles_cloup(self) -> dict[StyleId, CloupStyle]:
        return {sid: string_to_cloup(s) for sid, s in self.styles.items()}

    @cached_property
    def styles_fzf(self) -> dict[StyleId, str]:
        return {sid: string_to_fzf(s) for sid, s in self.styles.items()}


def _initialize_theme() -> Theme:
    name = os.getenv("EASYBORG_THEME", "melody_dark")
    return Theme.from_name(name)


_THEME = _initialize_theme()


def theme() -> Theme:
    if _THEME is None:
        raise RuntimeError("Theme not initialized")
    return _THEME
