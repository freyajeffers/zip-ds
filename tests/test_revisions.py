from zip_ds.models import DocumentChunk
from zip_ds.queries.models import SearchCandidate, SourceType
from zip_ds.queries.revisions import calculate_revision_delta, suppress_lineage_candidates


def chunk(chunk_id: str, chunk_hash: str) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        chunk_hash=chunk_hash,
        start_offset=0,
        end_offset=5,
        raw_text="alpha",
        token_count=1,
    )


def candidate(url: str, chunk_id: str = "chunk-1") -> SearchCandidate:
    return SearchCandidate(
        url=url,
        source_type=SourceType.WEB,
        rank_position=1,
        matched_query="alpha",
        originating_chunk_id=chunk_id,
    )


def test_revision_delta_reuses_unchanged_hashes():
    previous = [chunk("old-1", "a" * 64), chunk("old-2", "b" * 64)]
    current = [chunk("new-1", "a" * 64), chunk("new-2", "c" * 64)]

    delta = calculate_revision_delta(current, previous)

    assert delta.unchanged_chunk_ids == ["new-1"]
    assert [item.chunk_id for item in delta.modified_chunks] == ["new-2"]


def test_lineage_candidates_exclude_previous_draft_urls():
    candidates = [candidate("https://example.com/old"), candidate("https://example.com/new")]

    filtered = suppress_lineage_candidates(candidates, {"https://example.com/old"})

    assert [item.url for item in filtered] == ["https://example.com/new"]


def test_revision_boundaries_reject_duplicate_hashes():
    with __import__("pytest").raises(ValueError):
        calculate_revision_delta([chunk("one", "a" * 64), chunk("two", "a" * 64)], [])
