import math

import pytest

from zip_ds.chunking import make_chunk
from zip_ds.models import DocumentChunk, StyleScores
from zip_ds.queries.generator import generate_queries, query_budget, shingles
from zip_ds.queries.models import SearchCandidate, SourceType
from zip_ds.stylometry.analyzer import analyze


def test_style_scores_reject_non_finite_or_negative_values():
    with pytest.raises(ValueError):
        StyleScores(asl=-1)
    with pytest.raises(ValueError):
        StyleScores(awl=math.inf)


def test_document_chunk_rejects_invalid_contract_values():
    with pytest.raises(ValueError):
        DocumentChunk(
            chunk_id="id",
            chunk_hash="0" * 64,
            parent_chunk_id=None,
            start_offset=5,
            end_offset=4,
            raw_text="",
            token_count=0,
        )
    with pytest.raises(ValueError):
        DocumentChunk(
            chunk_id="id",
            chunk_hash="bad",
            parent_chunk_id=None,
            start_offset=0,
            end_offset=4,
            raw_text="text",
            token_count=-1,
        )
    with pytest.raises(ValueError):
        DocumentChunk(
            chunk_id="id",
            chunk_hash="0" * 64,
            parent_chunk_id=None,
            start_offset=0,
            end_offset=4,
            raw_text="text",
            token_count=1,
            is_bibliography="yes",
        )


def test_search_candidate_rejects_invalid_url_rank_and_score():
    fields = {
        "url": "not-a-url",
        "source_type": SourceType.WEB,
        "title": "title",
        "snippet": "snippet",
        "rank_position": 1,
        "matched_query": "query",
        "originating_chunk_id": "chunk",
    }
    with pytest.raises(ValueError):
        SearchCandidate(**fields)
    with pytest.raises(ValueError):
        SearchCandidate(**{**fields, "url": "https://example.test", "rank_position": 0})
    with pytest.raises(ValueError):
        SearchCandidate(**{**fields, "url": "https://example.test", "snippet_jaccard_score": 1.1})


@pytest.mark.parametrize("value", [None, 1, [], {}])
def test_text_apis_reject_non_string_input(value):
    with pytest.raises(TypeError):
        shingles(value)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        generate_queries(value)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        analyze(value)  # type: ignore[arg-type]


def test_query_apis_reject_invalid_numeric_parameters():
    with pytest.raises(ValueError):
        shingles("one two three", size=0)
    with pytest.raises(ValueError):
        shingles("one two three", step=0)
    with pytest.raises(ValueError):
        generate_queries("one two three", max_queries=-1)
    with pytest.raises(ValueError):
        query_budget(-1)


def test_make_chunk_validates_input_and_output_invariants():
    with pytest.raises(TypeError):
        make_chunk(1)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        make_chunk("text", start_offset=-1)
    chunk = make_chunk("text")
    assert chunk.chunk_hash == __import__("hashlib").sha256(b"text").hexdigest()
