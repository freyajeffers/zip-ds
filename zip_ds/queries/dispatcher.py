import json
import sqlite3
import time
from collections.abc import Awaitable, Callable
from hashlib import sha256
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

from zip_ds.queries.limiter import TokenBucket, TokenBucketSettings
from zip_ds.queries.models import SearchCandidate, SourceType


class QueryBudgetExceeded(RuntimeError):
    pass


class QueryBudget(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

    word_count: int = Field(ge=0)
    maximum: int | None = Field(default=None, ge=0)
    limit: int = Field(default=0, ge=0)
    used: int = Field(default=0, ge=0)

    @model_validator(mode="before")
    @classmethod
    def set_limit(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        values = dict(data)
        if values.get("limit") is None:
            word_count = values.get("word_count")
            maximum = values.get("maximum")
            if not isinstance(word_count, int) or word_count < 0:
                return values
            derived = min(45, max(3, int(3 + 0.008 * word_count + 0.999999)))
            values["limit"] = maximum if isinstance(maximum, int) else derived
        return values

    @model_validator(mode="after")
    def validate_state(self) -> QueryBudget:
        if self.maximum is not None and self.limit > self.maximum:
            raise ValueError("limit cannot exceed maximum")
        if self.used > self.limit:
            raise ValueError("used cannot exceed limit")
        return self

    def consume(self) -> None:
        if self.used >= self.limit:
            raise QueryBudgetExceeded(f"query budget exhausted ({self.limit})")
        self.used += 1

    @property
    def remaining(self) -> int:
        return self.limit - self.used


class SerpCacheSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    path: str = Field(min_length=1)
    ttl_seconds: int = Field(default=7 * 24 * 3600, ge=0)


class SerpCacheEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    query_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    query: str = Field(min_length=1)
    candidates: list[SearchCandidate]
    created_at: float = Field(ge=0)


class SerpCache:
    def __init__(self, path: str | Path, ttl_seconds: int = 7 * 24 * 3600) -> None:
        settings = SerpCacheSettings(path=str(path), ttl_seconds=ttl_seconds)
        self.path = settings.path
        self.ttl_seconds = settings.ttl_seconds
        self._connection = sqlite3.connect(self.path)
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._connection.execute("PRAGMA busy_timeout = 5000")
        self._connection.execute("PRAGMA synchronous = NORMAL")
        self._connection.execute("PRAGMA mmap_size = 268435456")
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS serp_cache (query_hash TEXT PRIMARY KEY, query TEXT NOT NULL, payload TEXT NOT NULL, created_at REAL NOT NULL)"
        )
        self._connection.commit()

    def get(self, query: str) -> list[SearchCandidate] | None:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        key = sha256(query.strip().lower().encode()).hexdigest()
        row = self._connection.execute(
            "SELECT payload, created_at FROM serp_cache WHERE query_hash = ?", (key,)
        ).fetchone()
        if row is None:
            return None
        raw_candidates = json.loads(row[0])
        candidates = [
            SearchCandidate(
                **{
                    **{k: v for k, v in item.items() if k not in {"title", "snippet"}},
                    "source_type": SourceType(item["source_type"]),
                }
            )
            for item in raw_candidates
        ]
        entry = SerpCacheEntry(
            query_hash=key,
            query=query,
            candidates=candidates,
            created_at=row[1],
        )
        if time.time() - entry.created_at > self.ttl_seconds:
            self._connection.execute("DELETE FROM serp_cache WHERE query_hash = ?", (key,))
            self._connection.commit()
            return None
        return entry.candidates

    def put(self, query: str, candidates: list[SearchCandidate]) -> None:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        if not isinstance(candidates, list) or not all(
            isinstance(item, SearchCandidate) for item in candidates
        ):
            raise TypeError("candidates must be a list of SearchCandidate models")
        key = sha256(query.strip().lower().encode()).hexdigest()
        entry = SerpCacheEntry(
            query_hash=key,
            query=query,
            candidates=candidates,
            created_at=time.time(),
        )
        payload = json.dumps(
            [
                item.model_dump(exclude={"title", "snippet"}, mode="json")
                for item in entry.candidates
            ]
        )
        self._connection.execute(
            "INSERT OR REPLACE INTO serp_cache VALUES (?, ?, ?, ?)",
            (entry.query_hash, entry.query, payload, entry.created_at),
        )
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()


async def dispatch_queries(
    queries: list[str],
    provider: Callable[[str], Awaitable[list[SearchCandidate]]],
    budget: QueryBudget,
    cache: SerpCache,
    limiter: TokenBucket | None = None,
) -> list[SearchCandidate]:
    if not isinstance(queries, list) or not all(
        isinstance(query, str) and query.strip() for query in queries
    ):
        raise TypeError("queries must be a list of non-empty strings")
    if not isinstance(budget, QueryBudget) or not isinstance(cache, SerpCache):
        raise TypeError("budget and cache must use their validated boundary types")
    if limiter is None:
        limiter = TokenBucket(TokenBucketSettings(capacity=20, refill_rate=20.0))
    elif not isinstance(limiter, TokenBucket):
        raise TypeError("limiter must be a TokenBucket")
    results: list[SearchCandidate] = []
    for query in queries:
        cached = cache.get(query)
        if cached is not None:
            results.extend(cached)
            continue
        await limiter.acquire()
        budget.consume()
        candidates = await provider(query)
        if not isinstance(candidates, list) or not all(
            isinstance(item, SearchCandidate) for item in candidates
        ):
            raise TypeError("provider must return a list of SearchCandidate models")
        cache.put(query, candidates)
        results.extend(candidates)
        if any(candidate.snippet_jaccard_score > 0.70 for candidate in candidates):
            break
    return results
