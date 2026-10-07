import asyncio
import json
from collections.abc import Awaitable, Callable
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from pydantic import ConfigDict, Field, field_validator

from zip_ds.models import SearchCandidate, SourceType, ValidatedModel
from zip_ds.queries.providers import ProviderClient, ProviderError, ProviderRateLimit


class SerpApiSettings(ValidatedModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    endpoint: str = Field(min_length=1)
    engine: str = Field(default="google", min_length=1)
    timeout: float = Field(default=5.0, gt=0.0)

    @field_validator("endpoint")
    @classmethod
    def require_http_endpoint(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("endpoint must be HTTP(S)")
        return value


def parse_serpapi_response(payload: str, query: str, chunk_id: str) -> list[SearchCandidate]:
    if not all(isinstance(value, str) and value for value in (payload, query, chunk_id)):
        raise TypeError("payload, query, and chunk_id must be non-empty strings")
    try:
        data = json.loads(payload)
        organic = data.get("organic_results", [])
    except (TypeError, json.JSONDecodeError) as exc:
        raise ProviderError("provider returned invalid JSON") from exc
    if not isinstance(organic, list):
        raise ProviderError("provider organic_results must be a list")
    candidates: list[SearchCandidate] = []
    for rank, item in enumerate(organic, start=1):
        if not isinstance(item, dict) or not isinstance(item.get("link"), str):
            continue
        try:
            candidates.append(
                SearchCandidate(
                    url=item["link"],
                    source_type=SourceType.WEB,
                    title=item.get("title", "") if isinstance(item.get("title", ""), str) else "",
                    snippet=(
                        item.get("snippet", "") if isinstance(item.get("snippet", ""), str) else ""
                    ),
                    rank_position=rank,
                    matched_query=query,
                    originating_chunk_id=chunk_id,
                )
            )
        except ValueError:
            continue
    return candidates


async def _default_transport(url: str) -> tuple[int, bytes]:
    def request() -> tuple[int, bytes]:
        try:
            with urlopen(Request(url, headers={"User-Agent": "ZIP-DS/0.1"})) as response:
                return response.status, response.read()
        except OSError as exc:
            raise ProviderError("provider request failed") from exc

    return await asyncio.to_thread(request)


class SerpApiProvider:
    """SerpAPI-compatible provider; the API key is held only for request construction."""

    def __init__(
        self,
        settings: SerpApiSettings,
        api_key: str,
        transport: Callable[[str], Awaitable[tuple[int, bytes]]] = _default_transport,
    ) -> None:
        if not isinstance(settings, SerpApiSettings):
            raise TypeError("settings must be SerpApiSettings")
        if not isinstance(api_key, str) or not api_key:
            raise ValueError("api_key must be non-empty")
        if not callable(transport):
            raise TypeError("transport must be callable")
        self.settings = settings
        self._api_key = api_key
        self._transport = transport

    async def search(self, query: str, chunk_id: str) -> list[SearchCandidate]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be non-empty")
        if not isinstance(chunk_id, str) or not chunk_id:
            raise ValueError("chunk_id must be non-empty")
        url = f"{self.settings.endpoint}?{urlencode({'engine': self.settings.engine, 'q': query, 'api_key': self._api_key})}"
        status, body = await self._transport(url)
        if status == 429:
            raise ProviderRateLimit("provider quota exceeded")
        if status >= 400:
            raise ProviderError(f"provider returned HTTP {status}")
        return parse_serpapi_response(body.decode("utf-8"), query, chunk_id)

    def as_client(self, chunk_id: str) -> ProviderClient:
        if not isinstance(chunk_id, str) or not chunk_id:
            raise ValueError("chunk_id must be non-empty")

        async def call(query: str) -> list[SearchCandidate]:
            return await self.search(query, chunk_id)

        return ProviderClient(name="serpapi", call=call)
