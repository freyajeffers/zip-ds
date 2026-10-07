import pytest

from zip_ds.alignment.lexical import align_lexically

SUSPICIOUS = (
    "Opening context " + "alpha beta gamma delta epsilon zeta eta theta" + " closing context"
)
SOURCE = "Source lead " + "alpha beta gamma delta epsilon zeta eta theta" + " source tail"


def test_align_lexically_returns_exact_match_offsets():
    matches = align_lexically(SUSPICIOUS, SOURCE, "https://example.com/source", "chunk-1")

    assert len(matches) == 1
    match = matches[0]
    assert match.matched_susp_text == "alpha beta gamma delta epsilon zeta eta theta"
    assert SUSPICIOUS[match.susp_start_char : match.susp_end_char] == match.matched_susp_text
    assert match.matched_source_text == match.matched_susp_text
    assert match.alignment_type == "verbatim"


def test_align_lexically_suppresses_matches_shorter_than_seven_words():
    matches = align_lexically(
        "alpha beta gamma delta epsilon zeta",
        "prefix alpha beta gamma delta epsilon zeta suffix",
        "https://example.com/source",
        "chunk-1",
    )

    assert matches == []


def test_align_lexically_rejects_invalid_boundary_values():
    with pytest.raises(ValueError):
        align_lexically("text", "source", "not-a-url", "chunk-1")
