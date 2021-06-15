from pystr.approx import Edit, edits_to_cigar, cigar_to_edits


def test_cigar_mapping() -> None:
    edits = [Edit.M, Edit.M, Edit.I, Edit.M, Edit.D]
    cigar = edits_to_cigar(edits)
    edits2 = cigar_to_edits(cigar)
    print(edits2)


test_cigar_mapping()
