import enum
import re


class Edit(enum.Enum):
    M = enum.auto()
    I = enum.auto()  # noqal: E741
    D = enum.auto()


def edits_to_cigar(edits: list[Edit]) -> str:
    res: list[str] = []
    i = 0
    while i < len(edits):
        j = i + 1
        while j < len(edits) and edits[i] == edits[j]:
            j += 1
        res.append(f"{j-i}{edits[i]!s}")
        i = j
    return ''.join(res)


def cigar_to_edits(cigar: str) -> list[Edit]:
    res: list[Edit] = []
    groups = re.findall(r"\d+\D", cigar, flags=re.ASCII)
    for group in groups:
        match = re.match(r"(\d+)(\D)", group)
        assert match is not None
        n, e = match.groups()
        res.extend([Edit[e]] * int(n))
    return res


def extract_alignment(x: str, p: str, pos: int, cigar: str) -> tuple[str, str]:
    i, j = pos, 0
    x_, p_ = [], []
    for edit in cigar_to_edits(cigar):
        if edit == Edit.M:
            x_.append(x[i])
            i += 1
            p_.append(p[j])
            j += 1
        if edit == Edit.I:
            x_.append('-')
            p_.append(p[j])
            j += 1
        if edit == Edit.D:
            x_.append(x[i])
            i += 1
            p_.append('-')
    return ''.join(x_), ''.join(p_)


def count_edits(alignment: tuple[str, str]) -> int:
    return sum(a != b for a, b in zip(*alignment))
