"""Functionality for approximate matching."""

import enum
import re


class Edit(enum.Enum):
    """Edit operations."""

    Match = enum.auto()
    Insert = enum.auto()
    Delete = enum.auto()


EDIT_TO_CIGAR_MAP = {
    Edit.Match: "M",
    Edit.Insert: "I",
    Edit.Delete: "D"
}
CIGAR_TO_EDIT_MAP = {
    "M": Edit.Match,
    "I": Edit.Insert,
    "D": Edit.Delete
}


def edits_to_cigar(edits: list[Edit]) -> str:
    """Translate a list of edits into a cigar."""
    res: list[str] = []
    i = 0
    while i < len(edits):
        j = i + 1
        while j < len(edits) and edits[i] == edits[j]:
            j += 1
        res.append(f"{j-i}{EDIT_TO_CIGAR_MAP[edits[i]]}")
        i = j
    return ''.join(res)


def cigar_to_edits(cigar: str) -> list[Edit]:
    """Translate a cigar into a list of edits."""
    res: list[Edit] = []
    groups = re.findall(r"\d+\D", cigar, flags=re.ASCII)
    for group in groups:
        match = re.match(r"(\d+)(\D)", group)
        assert match is not None
        num, edit = match.groups()
        res.extend([CIGAR_TO_EDIT_MAP[edit]] * int(num))
    return res


def extract_alignment(x: str, p: str, pos: int, cigar: str) -> tuple[str, str]:
    """Extract a local alignment from a string, read, position and cigar."""
    i, j = pos, 0
    x_, p_ = [], []
    for edit in cigar_to_edits(cigar):
        if edit == Edit.Match:
            x_.append(x[i])
            i += 1
            p_.append(p[j])
            j += 1
        if edit == Edit.Insert:
            x_.append('-')
            p_.append(p[j])
            j += 1
        if edit == Edit.Delete:
            x_.append(x[i])
            i += 1
            p_.append('-')
    return ''.join(x_), ''.join(p_)


def count_edits(alignment: tuple[str, str]) -> int:
    """Count how many edits we see in an alignment."""
    return sum(a != b for a, b in zip(*alignment))
