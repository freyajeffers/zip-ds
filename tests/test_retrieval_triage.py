import pytest

from zip_ds.queries.models import SearchCandidate, SourceType
from zip_ds.retrieval.triage import should_retrieve_candidate, snippet_jaccard


def _candidate(snippet: str) -> SearchCandidate:
    return SearchCandidate(
        url="https://example.com/source",
        source_type=SourceType.WEB,
        title="source",
        snippet=snippet,
        rank_position=1,
        matched_query='"shared language"',
        originating_chunk_id="chunk-1",
    )


def test_snippet_jaccard_uses_three_word_grams():
    assert snippet_jaccard("alpha beta gamma delta", "alpha beta gamma epsilon") == 1 / 3


def test_should_retrieve_candidate_when_score_meets_threshold():
    candidate = _candidate("alpha beta gamma delta")

    assert should_retrieve_candidate(candidate, "alpha beta gamma epsilon") is True


def test_should_not_retrieve_candidate_below_threshold():
    candidate = _candidate("unrelated words only")

    assert should_retrieve_candidate(candidate, "alpha beta gamma epsilon") is False


def test_short_text_without_three_grams_has_zero_similarity():
    assert snippet_jaccard("alpha beta", "alpha beta") == 0.0


def test_should_retrieve_candidate_rejects_invalid_boundary_values():
    candidate = _candidate("alpha beta gamma")

    with pytest.raises(ValueError):
        should_retrieve_candidate(candidate, "alpha beta gamma", threshold=2.0)
