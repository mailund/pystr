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
        res.append(f"{j-i}{edits[i]}")
        i = j
    return ''.join(res)


def cigar_to_edits(cigar: str) -> list[Edit]:
    res: list[Edit] = []
    groups = re.findall(r"\d+\D", cigar, flags=re.ASCII)
    for group in groups:
        match = re.match(r"(\d+)(\D)", group)
        assert match is not None
        n, e = match.groups()
        n, e = int(n), Edit[e]
        res.extend([e] * n)
    return res
