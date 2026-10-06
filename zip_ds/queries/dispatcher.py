import json
import sqlite3
import time
from collections.abc import Awaitable, Callable
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path

from zip_ds.queries.models import SearchCandidate, SourceType


class QueryBudgetExceeded(RuntimeError):
    pass


class QueryBudget:
    def __init__(self, word_count: int, maximum: int | None = None) -> None:
        self.limit = (
            maximum
            if maximum is not None
            else min(45, max(3, int(3 + 0.008 * word_count + 0.999999)))
        )
        self.used = 0

    def consume(self) -> None:
        if self.used >= self.limit:
            raise QueryBudgetExceeded(f"query budget exhausted ({self.limit})")
        self.used += 1

    @property
    def remaining(self) -> int:
        return self.limit - self.used


class SerpCache:
    def __init__(self, path: str | Path, ttl_seconds: int = 7 * 24 * 3600) -> None:
        self.path = str(path)
        self.ttl_seconds = ttl_seconds
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
        key = sha256(query.strip().lower().encode()).hexdigest()
        row = self._connection.execute(
            "SELECT payload, created_at FROM serp_cache WHERE query_hash = ?", (key,)
        ).fetchone()
        if row is None:
            return None
        if time.time() - row[1] > self.ttl_seconds:
            self._connection.execute("DELETE FROM serp_cache WHERE query_hash = ?", (key,))
            self._connection.commit()
            return None
        return [
            SearchCandidate(
                source_type=SourceType(item["source_type"]),
                **{k: v for k, v in item.items() if k != "source_type"},
            )
            for item in json.loads(row[0])
        ]

    def put(self, query: str, candidates: list[SearchCandidate]) -> None:
        key = sha256(query.strip().lower().encode()).hexdigest()
        payload = json.dumps(
            [{**asdict(item), "source_type": item.source_type.value} for item in candidates]
        )
        self._connection.execute(
            "INSERT OR REPLACE INTO serp_cache VALUES (?, ?, ?, ?)",
            (key, query, payload, time.time()),
        )
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()


async def dispatch_queries(
    queries: list[str],
    provider: Callable[[str], Awaitable[list[SearchCandidate]]],
    budget: QueryBudget,
    cache: SerpCache,
) -> list[SearchCandidate]:
    results: list[SearchCandidate] = []
    for query in queries:
        cached = cache.get(query)
        if cached is not None:
            results.extend(cached)
            continue
        budget.consume()
        candidates = await provider(query)
        cache.put(query, candidates)
        results.extend(candidates)
        if any(candidate.snippet_jaccard_score > 0.70 for candidate in candidates):
            break
    return results
