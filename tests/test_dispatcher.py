import asyncio

import pytest

from zip_ds.queries.dispatcher import QueryBudget, QueryBudgetExceeded, SerpCache, dispatch_queries
from zip_ds.queries.models import SearchCandidate, SourceType


def candidate(query: str, score: float = 0.1) -> SearchCandidate:
    return SearchCandidate(
        url=f"https://example.test/{query}",
        source_type=SourceType.WEB,
        title="Example",
        snippet="snippet",
        rank_position=1,
        matched_query=query,
        originating_chunk_id="chunk-1",
        snippet_jaccard_score=score,
    )


def test_budget_enforces_limit():
    budget = QueryBudget(100, maximum=1)
    budget.consume()
    with pytest.raises(QueryBudgetExceeded):
        budget.consume()


def test_cache_round_trip_and_normalized_key(tmp_path):
    cache = SerpCache(tmp_path / "serp.db")
    cache.put(" Test Query ", [candidate("Test Query")])
    cached = cache.get("test query")
    assert cached is not None
    assert cached[0].url == "https://example.test/Test Query"
    cache.close()


def test_dispatch_uses_cache_and_adaptive_stop(tmp_path):
    cache = SerpCache(tmp_path / "serp.db")
    calls: list[str] = []

    async def provider(query: str) -> list[SearchCandidate]:
        calls.append(query)
        return [candidate(query, score=0.8)]

    results = asyncio.run(dispatch_queries(["a", "b"], provider, QueryBudget(100), cache))
    assert len(results) == 1
    assert calls == ["a"]
    asyncio.run(dispatch_queries(["a"], provider, QueryBudget(100), cache))
    assert calls == ["a"]
    cache.close()
