import asyncio

from zip_ds.chunking import make_chunk
from zip_ds.models import SearchCandidate, SourceType
from zip_ds.pipeline import run_revision_scan
from zip_ds.queries.reuse import RevisionEvidence
from zip_ds.reporting import AlignmentEvidence


def test_revision_scan_reuses_cached_results_without_retrieval():
    text = "The cat quickly crossed the quiet garden before sunrise."
    prior = make_chunk(text)
    cached = RevisionEvidence(
        chunk_hash=prior.chunk_hash,
        evidence=[
            AlignmentEvidence(
                suspicious_chunk_id=prior.chunk_id,
                source_url="https://example.com/prior",
                alignment_type="verbatim",
                matched_word_count=8,
                confidence_score=1.0,
            )
        ],
    )

    async def fail_retriever(_candidates, _text):
        raise AssertionError("unchanged revision must not retrieve candidates")

    report = asyncio.run(
        run_revision_scan("doc-2", text, [prior], [cached], [], retriever=fail_retriever)
    )

    assert report.evidence[0].source_url == "https://example.com/prior"
    assert report.evidence[0].suspicious_chunk_id != prior.chunk_id


def test_revision_scan_suppresses_prior_lineage_candidates():
    text = "The cat quickly crossed the quiet garden before sunrise."
    candidate = SearchCandidate(
        url="https://example.com/current",
        source_type=SourceType.WEB,
        title="current",
        snippet=text,
        rank_position=1,
        matched_query="cat garden",
        originating_chunk_id="chunk-1",
    )
    seen = []

    async def retriever(candidates, _text):
        seen.extend(candidates)
        return []

    asyncio.run(
        run_revision_scan(
            "doc-3",
            text,
            [],
            [],
            [candidate],
            excluded_lineage_urls={"https://example.com/old"},
            retriever=retriever,
        )
    )
    assert seen == [candidate]
