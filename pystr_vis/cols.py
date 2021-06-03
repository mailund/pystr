from __future__ import annotations
import re

RESET = "\u001b[0m"

strip_ANSI_escapes = re.compile(r"""
    \u001b\[  # The escape code, then
    [;\d]*    # zero or more digits or semicolons,
    [A-Za-z]  # followed by a letter (FIXME: don't know if only m?)
    """, re.VERBOSE).sub


def strip_ansi(s: str) -> str:
    return strip_ANSI_escapes("", s)


def ansifree_len(s: str) -> int:
    return len(strip_ansi(s))


def ansi_align_left(x: str, w: int) -> str:
    return x + ' ' * (w - ansifree_len(x))


def ansi_align_right(x: str, w: int) -> str:
    return ' ' * (w - ansifree_len(x)) + x


class Colour:
    ansi_code: str

    def __init__(self, ansi_code: str) -> None:
        self.ansi_code = ansi_code

    def __call__(self, s: str) -> str:
        x = str(s)
        return f"{self}{x}{RESET}"

    def __and__(self, other: Colour) -> Colour:
        return Colour(self.ansi_code + other.ansi_code)

    def __str__(self) -> str:
        return self.ansi_code


black = Colour("\u001b[30m")
red = Colour("\u001b[31m")
green = Colour("\u001b[32m")
yellow = Colour("\u001b[33m")
blue = Colour("\u001b[34m")
magenta = Colour("\u001b[35m")
cyan = Colour("\u001b[36m")
white = Colour("\u001b[37m")

bright_black = Colour("\u001b[30;1m")
bright_red = Colour("\u001b[31;1m")
bright_green = Colour("\u001b[32;1m")
bright_yellow = Colour("\u001b[33;1m")
bright_blue = Colour("\u001b[34;1m")
bright_magenta = Colour("\u001b[35;1m")
bright_cyan = Colour("\u001b[36;1m")
bright_white = Colour("\u001b[37;1m")

bold = Colour("\u001b[1m")
underline = Colour("\u001b[4m")
reverse = Colour("\u001b[7m")

# This is a bit of a hack to represent no formatting
plain = Colour(RESET)
