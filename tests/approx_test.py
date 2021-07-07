"""Testing approximative matching support code."""

from pystr.approx import (
    Edit,
    edits_to_cigar, cigar_to_edits,
    extract_alignment, count_edits
)


def test_cigar_mapping() -> None:
    """Test that we can make a list of edits into a cigar."""
    edits = [Edit.MATCH, Edit.MATCH, Edit.INSERT, Edit.MATCH, Edit.DELETE]
    cigar = edits_to_cigar(edits)
    edits2 = cigar_to_edits(cigar)
    assert edits == edits2


def test_extract_and_count() -> None:
    """Test that we count the right edits."""
    assert count_edits(
        extract_alignment('aacgt', 'agt', 1, '1M1D1M')
    ) == 1
