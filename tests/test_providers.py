import asyncio

import pytest

from zip_ds.queries.models import SearchCandidate, SourceType
from zip_ds.queries.providers import ProviderClient, ProviderManager, ProviderRateLimit


def candidate(query: str) -> SearchCandidate:
    return SearchCandidate(
        url="https://example.com/source",
        source_type=SourceType.WEB,
        rank_position=1,
        matched_query=query,
        originating_chunk_id="chunk-1",
    )


def test_provider_manager_fails_over_and_cools_rate_limited_provider():
    now = [100.0]
    calls: list[str] = []

    async def primary(query: str) -> list[SearchCandidate]:
        calls.append("primary")
        raise ProviderRateLimit("quota")

    async def secondary(query: str) -> list[SearchCandidate]:
        calls.append("secondary")
        return [candidate(query)]

    manager = ProviderManager(
        [
            ProviderClient(name="primary", call=primary),
            ProviderClient(name="secondary", call=secondary),
        ],
        cooldown=10.0,
        clock=lambda: now[0],
    )

    assert asyncio.run(manager.search("query"))[0].matched_query == "query"
    assert calls == ["primary", "secondary"]
    assert asyncio.run(manager.search("query"))[0].matched_query == "query"
    assert calls == ["primary", "secondary", "secondary"]


def test_provider_manager_rejects_empty_provider_list():
    with pytest.raises(ValueError):
        ProviderManager([])
