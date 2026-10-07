import asyncio

from zip_ds.chunking import make_chunk
from zip_ds.models import SearchCandidate, SourceType
from zip_ds.pipeline import run_revision_scan
from zip_ds.queries.revision_cache import RevisionCache


def test_revision_scan_reads_and_writes_revision_cache(tmp_path):
    text = "The cat quickly crossed the quiet garden before sunrise."
    cache = RevisionCache(tmp_path / "revision.db")
    candidate = SearchCandidate(
        url="https://example.com/source",
        source_type=SourceType.WEB,
        title="source",
        snippet=text,
        rank_position=1,
        matched_query="cat garden",
        originating_chunk_id="chunk-1",
    )
    calls = 0

    async def retriever(_candidates, _text):
        nonlocal calls
        calls += 1
        from zip_ds.retrieval import EphemeralSource

        return [EphemeralSource(source_url=candidate.url, text=text)]

    first = asyncio.run(
        run_revision_scan("doc", text, [], [], [candidate], cache=cache, retriever=retriever)
    )
    prior = make_chunk(text)
    second = asyncio.run(
        run_revision_scan(
            "doc",
            text,
            [prior],
            [],
            [],
            cache=cache,
            retriever=retriever,
        )
    )

    assert calls == 1
    assert first.evidence[0].model_copy(update={"suspicious_chunk_id": "same"}) == second.evidence[
        0
    ].model_copy(update={"suspicious_chunk_id": "same"})
    cache.close()
