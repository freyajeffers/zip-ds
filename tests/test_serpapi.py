import asyncio

import pytest

from zip_ds.queries.providers import ProviderRateLimit
from zip_ds.queries.serpapi import SerpApiProvider, SerpApiSettings, parse_serpapi_response

PAYLOAD = (
    '{"organic_results": [{"link": "https://example.com/a", "title": "A", "snippet": "alpha"}]}'
)


def test_parse_serpapi_response_creates_privacy_safe_candidates():
    results = parse_serpapi_response(PAYLOAD, "alpha", "chunk-1")

    assert len(results) == 1
    assert results[0].url == "https://example.com/a"
    assert results[0].title == "A"
    assert results[0].matched_query == "alpha"


def test_serpapi_provider_maps_rate_limits():
    async def transport(url: str) -> tuple[int, bytes]:
        return 429, b"quota"

    provider = SerpApiProvider(
        SerpApiSettings(endpoint="https://serpapi.example/search"),
        "secret",
        transport=transport,
    )

    with pytest.raises(ProviderRateLimit):
        asyncio.run(provider.search("alpha", "chunk-1"))


def test_serpapi_settings_reject_invalid_endpoint():
    with pytest.raises(ValueError):
        SerpApiSettings(endpoint="not-a-url")
