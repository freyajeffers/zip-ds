import asyncio
import logging
import re
from html.parser import HTMLParser
from typing import cast
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from pydantic import BaseModel, ConfigDict, Field, field_validator

from zip_ds.queries.models import SearchCandidate
from zip_ds.retrieval.triage import should_retrieve_candidate

logger = logging.getLogger(__name__)
_MAX_RESPONSE_BYTES = 2_000_000
_WHITESPACE = re.compile(r"\s+")
_SKIP_TAGS = {"aside", "footer", "header", "nav", "noscript", "script", "style"}


class EphemeralSource(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    source_url: str = Field(min_length=1)
    source_title: str = ""
    text: str = Field(min_length=1)

    @field_validator("source_url")
    @classmethod
    def require_http_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("source_url must be HTTP(S)")
        return value


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._in_title = False
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized = tag.casefold()
        if normalized == "title":
            self._in_title = True
        if normalized in _SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.casefold()
        if normalized == "title":
            self._in_title = False
        if normalized in _SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        elif not self._skip_depth:
            self.text_parts.append(data)


def _clean(parts: list[str]) -> str:
    return _WHITESPACE.sub(" ", " ".join(parts)).strip()


def extract_html_text(html: str, source_url: str) -> EphemeralSource:
    if not isinstance(html, str):
        raise TypeError("html must be a string")
    parser = _TextExtractor()
    parser.feed(html)
    parser.close()
    text = _clean(parser.text_parts)
    if not text:
        raise ValueError("source HTML contains no extractable text")
    return EphemeralSource(
        source_url=source_url, source_title=_clean(parser.title_parts), text=text
    )


def _fetch_bytes(url: str, timeout: float) -> bytes:
    request = Request(url, headers={"User-Agent": "ZIP-DS/0.1"})
    with urlopen(request, timeout=timeout) as response:
        body = cast(bytes, response.read(_MAX_RESPONSE_BYTES + 1))
    if len(body) > _MAX_RESPONSE_BYTES:
        raise ValueError("source response exceeds the in-memory size limit")
    return body


async def fetch_candidate(
    candidate: SearchCandidate, timeout: float = 5.0
) -> EphemeralSource | None:
    if not isinstance(candidate, SearchCandidate):
        raise TypeError("candidate must be a SearchCandidate model")
    if not isinstance(timeout, float) or timeout <= 0.0:
        raise ValueError("timeout must be a positive float")
    try:
        body = await asyncio.to_thread(_fetch_bytes, candidate.url, timeout)
        return extract_html_text(body.decode("utf-8", errors="replace"), candidate.url)
    except (OSError, TimeoutError, ValueError, UnicodeError) as exc:
        logger.debug("Skipping candidate %s after retrieval failure: %s", candidate.url, exc)
        return None


async def retrieve_candidates(
    candidates: list[SearchCandidate],
    suspicious_text: str,
    max_concurrency: int = 15,
    timeout: float = 5.0,
) -> list[EphemeralSource]:
    if not isinstance(candidates, list) or not all(
        isinstance(item, SearchCandidate) for item in candidates
    ):
        raise TypeError("candidates must be a list of SearchCandidate models")
    if not isinstance(max_concurrency, int) or max_concurrency < 1:
        raise ValueError("max_concurrency must be a positive integer")
    eligible = [item for item in candidates if should_retrieve_candidate(item, suspicious_text)]
    semaphore = asyncio.Semaphore(max_concurrency)

    async def bounded_fetch(candidate: SearchCandidate) -> EphemeralSource | None:
        async with semaphore:
            return await fetch_candidate(candidate, timeout)

    results = await asyncio.gather(*(bounded_fetch(candidate) for candidate in eligible))
    return [result for result in results if result is not None]
