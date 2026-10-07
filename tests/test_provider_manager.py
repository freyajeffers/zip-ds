import asyncio

import pytest

from zip_ds.queries.models import SearchCandidate, SourceType
from zip_ds.queries.providers import (
    ProviderClient,
    ProviderError,
    ProviderManager,
    ProviderRateLimit,
)


async def _raise_rate(query: str):
    raise ProviderRateLimit("429")


async def _return_ok(query: str):
    return [
        SearchCandidate(
            url="https://example.com/ok",
            source_type=SourceType.WEB,
            title="ok",
            snippet=query,
            rank_position=1,
            matched_query=query,
            originating_chunk_id="c1",
        )
    ]


def test_failover_and_cooldown_behavior():
    # controlled clock
    now = 1000.0

    def clock():
        return now

    primary = ProviderClient(name="primary", call=_raise_rate)
    secondary = ProviderClient(name="secondary", call=_return_ok)

    manager = ProviderManager([primary, secondary], cooldown=30.0, clock=clock)

    # first search: primary rate-limits -> secondary returns
    results = asyncio.run(manager.search("q"))
    assert results[0].url == "https://example.com/ok"

    # primary should be cooled
    assert any(s.client.name == "primary" and s.failed_until > clock() for s in manager._states)
    assert manager.statuses()[0].available is False

    # advance time beyond cooldown: primary becomes retryable, but still raises RateLimit -> secondary used again
    now += 31.0
    results = asyncio.run(manager.search("q2"))
    assert results[0].matched_query == "q2"


def test_all_providers_fail_raises_providererror():
    async def _raise_other(query: str):
        raise RuntimeError("network")

    primary = ProviderClient(name="p", call=_raise_rate)
    secondary = ProviderClient(name="s", call=_raise_other)

    manager = ProviderManager([primary, secondary], cooldown=10.0, clock=lambda: 0.0)

    with pytest.raises(ProviderError):
        asyncio.run(manager.search("x"))
