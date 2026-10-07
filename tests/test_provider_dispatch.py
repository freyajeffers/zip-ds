import asyncio

from zip_ds.queries.dispatcher import QueryBudget, SerpCache, dispatch_queries
from zip_ds.queries.providers import ProviderManager
from zip_ds.queries.serpapi import SerpApiProvider, SerpApiSettings


def test_provider_client_can_be_wired_into_dispatcher(tmp_path):
    async def transport(url: str) -> tuple[int, bytes]:
        return 200, b'{"organic_results": [{"link": "https://example.com/a"}]}'

    provider = SerpApiProvider(
        SerpApiSettings(endpoint="https://serpapi.example/search"),
        "secret",
        transport=transport,
    )
    manager = ProviderManager([provider.as_client("chunk-1")])
    cache = SerpCache(tmp_path / "cache.db")

    results = asyncio.run(
        dispatch_queries(
            ["alpha"],
            manager.search,
            QueryBudget(word_count=10),
            cache,
        )
    )

    assert results[0].originating_chunk_id == "chunk-1"
    cache.close()
