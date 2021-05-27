from typing import Any


class Colour:
    ansi_code: str

    def __init__(self, ansi_code: str):
        self.ansi_code = ansi_code

    def __call__(self, s: Any) -> str:
        return f"{self}{str(s)}{RESET}"

    def __str__(self):
        return self.ansi_code


black          = Colour("\u001b[30m")    # noqa: E221
red            = Colour("\u001b[31m")    # noqa: E221
green          = Colour("\u001b[32m")    # noqa: E221
yellow         = Colour("\u001b[33m")    # noqa: E221
blue           = Colour("\u001b[34m")    # noqa: E221
magenta        = Colour("\u001b[35m")    # noqa: E221
cyan           = Colour("\u001b[36m")    # noqa: E221
white          = Colour("\u001b[37m")    # noqa: E221

bright_black   = Colour("\u001b[30;1m")  # noqa: E221
bright_red     = Colour("\u001b[31;1m")  # noqa: E221
bright_green   = Colour("\u001b[32;1m")  # noqa: E221
bright_yellow  = Colour("\u001b[33;1m")  # noqa: E221
bright_blue    = Colour("\u001b[34;1m")  # noqa: E221
bright_magenta = Colour("\u001b[35;1m")  # noqa: E221
bright_cyan    = Colour("\u001b[36;1m")  # noqa: E221
bright_white   = Colour("\u001b[37;1m")  # noqa: E221

bold           = Colour("\u001b[1m")     # noqa: E221
underline      = Colour("\u001b[4m")     # noqa: E221
reverse        = Colour("\u001b[7m")     # noqa: E221

RESET = "\u001b[0m"
