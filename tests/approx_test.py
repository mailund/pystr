from pystr.approx import (
    Edit,
    edits_to_cigar, cigar_to_edits,
    extract_alignment, count_edits
)


def test_cigar_mapping() -> None:
    edits = [Edit.M, Edit.M, Edit.I, Edit.M, Edit.D]
    cigar = edits_to_cigar(edits)
    print(cigar)
    edits2 = cigar_to_edits(cigar)
    print(edits2)
    assert edits == edits2


def test_extract_and_count() -> None:
    assert 1 == count_edits(
        extract_alignment('aacgt', 'agt', 1, '1M1D1M')
    )
