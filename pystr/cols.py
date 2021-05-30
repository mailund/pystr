
RESET = "\u001b[0m"


# Remember the original length when we colour a string
class ColouredString:
    x: str
    orig_len: int

    def __init__(self, x: str, orig_len: int):
        self.x = x
        self.orig_len = orig_len

    def __str__(self):
        return self.x

    def __len__(self):
        return self.orig_len


class Colour:
    ansi_code: str

    def __init__(self, ansi_code: str):
        self.ansi_code = ansi_code

    def __call__(self, s: str) -> ColouredString:
        x = str(s)
        return ColouredString(f"{self}{x}{RESET}", len(x))

    def __str__(self):
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
