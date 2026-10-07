import asyncio

from zip_ds.chunking import make_chunk
from zip_ds.models import DocumentChunk, SearchCandidate, SourceType
from zip_ds.pipeline import run_revision_scan_chunks
from zip_ds.queries.reuse import RevisionEvidence
from zip_ds.queries.revision_cache import RevisionCache
from zip_ds.reporting import AlignmentEvidence


def _candidate_for(
    chunk: DocumentChunk, url: str = "https://example.com/source"
) -> SearchCandidate:
    return SearchCandidate(
        url=url,
        source_type=SourceType.WEB,
        title="source",
        snippet=chunk.raw_text,
        rank_position=1,
        matched_query="query",
        originating_chunk_id=chunk.chunk_id,
    )


def test_multi_chunk_revision_reuses_cached_and_fetches_pending(tmp_path):
    # two chunks: one cached, one modified
    text_a = "Alpha beta gamma delta epsilon zeta eta theta iota."
    text_b = "Epsilon zeta eta theta iota kappa lambda mu nu."
    chunk_a = make_chunk(text_a)
    chunk_b = make_chunk(text_b)

    cache = RevisionCache(tmp_path / "revision.db")

    # Put prior evidence for chunk_a
    prior_evidence = RevisionEvidence(
        chunk_hash=chunk_a.chunk_hash,
        evidence=[
            AlignmentEvidence(
                suspicious_chunk_id=chunk_a.chunk_id,
                source_url="https://example.com/prior-a",
                alignment_type="verbatim",
                matched_word_count=4,
                confidence_score=1.0,
            )
        ],
    )
    cache.put(prior_evidence)

    # Candidate belongs to chunk_b only
    candidate_b = _candidate_for(chunk_b, url="https://example.com/current-b")

    calls = 0

    async def retriever(candidates, suspicious_text):
        nonlocal calls
        calls += 1
        from zip_ds.retrieval import EphemeralSource

        # return ephemeral source for the candidate
        return [EphemeralSource(source_url=candidates[0].url, text=chunk_b.raw_text)]

    report = asyncio.run(
        run_revision_scan_chunks(
            "doc-multi",
            [chunk_a, chunk_b],
            previous_chunks=[chunk_a],
            cached_results=[],
            candidates=[candidate_b],
            cache=cache,
            retriever=retriever,
        )
    )

    # Only one retrieval for chunk_b
    assert calls == 1
    urls = {e.source_url for e in report.evidence}
    assert "https://example.com/prior-a" in urls
    assert "https://example.com/current-b" in urls
    cache.close()
