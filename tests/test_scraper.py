import asyncio

import pytest

from zip_ds.queries.models import SearchCandidate, SourceType
from zip_ds.retrieval.scraper import (
    EphemeralSource,
    extract_html_text,
    fetch_candidate,
    retrieve_candidates,
)


def test_extract_html_text_discards_script_style_and_navigation():
    html = """
    <html><head><title>Example title</title><style>.ad {}</style></head>
    <body><nav>Menu noise</nav><main>Alpha <b>beta</b> gamma.</main>
    <script>tracking()</script></body></html>
    """

    result = extract_html_text(html, "https://example.com/source")

    assert result.source_title == "Example title"
    assert result.text == "Alpha beta gamma."
    assert "tracking" not in result.text
    assert "Menu noise" not in result.text


def test_extract_html_text_rejects_invalid_source_url():
    with pytest.raises(ValueError):
        extract_html_text("<main>text</main>", "not-a-url")


def test_extract_html_text_rejects_non_string_html():
    with pytest.raises(TypeError):
        extract_html_text(123, "https://example.com/source")


def test_extract_html_text_rejects_empty_text():
    with pytest.raises(ValueError):
        extract_html_text("<main><style>noise</style></main>", "https://example.com/source")


def _candidate(snippet: str, url: str = "https://example.com/source") -> SearchCandidate:
    return SearchCandidate(
        url=url,
        source_type=SourceType.WEB,
        rank_position=1,
        matched_query="shared language",
        originating_chunk_id="chunk-1",
        snippet=snippet,
    )


def test_fetch_candidate_returns_ephemeral_source(monkeypatch):
    monkeypatch.setattr(
        "zip_ds.retrieval.scraper._fetch_bytes",
        lambda url, timeout: b"<title>Source</title><main>alpha beta</main>",
    )

    result = asyncio.run(fetch_candidate(_candidate("alpha beta")))

    assert isinstance(result, EphemeralSource)
    assert result.text == "alpha beta"


def test_fetch_candidate_rejects_invalid_inputs():
    with pytest.raises(TypeError):
        asyncio.run(fetch_candidate("not-a-candidate"))
    with pytest.raises(ValueError):
        asyncio.run(fetch_candidate(_candidate("alpha beta"), timeout=0.0))


def test_retrieve_candidates_applies_triage_and_concurrency(monkeypatch):
    calls: list[str] = []

    async def fake_fetch(candidate: SearchCandidate, timeout: float = 5.0) -> EphemeralSource:
        calls.append(candidate.url)
        return EphemeralSource(source_url=candidate.url, text="retrieved")

    monkeypatch.setattr("zip_ds.retrieval.scraper.fetch_candidate", fake_fetch)
    candidates = [
        _candidate("alpha beta gamma", "https://example.com/eligible"),
        _candidate("unrelated"),
    ]

    results = asyncio.run(
        retrieve_candidates(candidates, "alpha beta gamma", max_concurrency=1, timeout=2.0)
    )

    assert [result.source_url for result in results] == ["https://example.com/eligible"]
    assert calls == ["https://example.com/eligible"]
