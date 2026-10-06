import asyncio
import time

import pytest

from zip_ds.queries.dispatcher import QueryBudget, QueryBudgetExceeded, SerpCache, dispatch_queries
from zip_ds.queries.models import SearchCandidate, SourceType


def make_candidate(query: str, score: float = 0.0) -> SearchCandidate:
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


def test_budget_rejects_negative_and_exhausted_limits():
    with pytest.raises(ValueError):
        QueryBudget(10, maximum=-1)
    budget = QueryBudget(10, maximum=1)
    assert budget.remaining == 1
    budget.consume()
    assert budget.used == 1
    assert budget.remaining == 0
    with pytest.raises(QueryBudgetExceeded):
        budget.consume()


def test_cache_applies_ttl_and_does_not_reuse_expired_rows(tmp_path):
    cache = SerpCache(tmp_path / "serp.db", ttl_seconds=1)
    cache.put("Query", [make_candidate("Query")])
    assert cache.get(" query ")
    cache._connection.execute("UPDATE serp_cache SET created_at = ?", (time.time() - 2,))
    cache._connection.commit()
    assert cache.get("query") is None
    assert cache._connection.execute("SELECT count(*) FROM serp_cache").fetchone()[0] == 0
    cache.close()


def test_cache_configures_required_sqlite_pragmas(tmp_path):
    cache = SerpCache(tmp_path / "serp.db")
    assert cache._connection.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
    assert cache._connection.execute("PRAGMA busy_timeout").fetchone()[0] == 5000
    assert cache._connection.execute("PRAGMA synchronous").fetchone()[0] == 1
    cache.close()


def test_dispatch_does_not_consume_budget_for_cache_hits(tmp_path):
    cache = SerpCache(tmp_path / "serp.db")
    cache.put("cached", [make_candidate("cached")])
    calls: list[str] = []

    async def provider(query: str) -> list[SearchCandidate]:
        calls.append(query)
        return [make_candidate(query)]

    budget = QueryBudget(10, maximum=1)
    results = asyncio.run(dispatch_queries(["cached", "new"], provider, budget, cache))
    assert [item.matched_query for item in results] == ["cached", "new"]
    assert calls == ["new"]
    assert budget.used == 1
    cache.close()


def test_dispatch_stops_before_later_queries_when_overlap_is_verified(tmp_path):
    cache = SerpCache(tmp_path / "serp.db")
    calls: list[str] = []

    async def provider(query: str) -> list[SearchCandidate]:
        calls.append(query)
        return [make_candidate(query, score=0.71)]

    results = asyncio.run(dispatch_queries(["a", "b", "c"], provider, QueryBudget(100), cache))
    assert len(results) == 1
    assert calls == ["a"]
    cache.close()


def test_cache_round_trip_preserves_enum_and_all_fields(tmp_path):
    cache = SerpCache(tmp_path / "serp.db")
    original = make_candidate("query", score=0.42)
    cache.put("query", [original])
    assert cache.get("query") == [original]
    cache.close()
