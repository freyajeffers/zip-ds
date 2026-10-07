import json
import sqlite3
from pathlib import Path

from pydantic import Field

from zip_ds.models import ValidatedModel
from zip_ds.queries.reuse import RevisionEvidence


class RevisionCacheSettings(ValidatedModel):
    path: str = Field(min_length=1)


class RevisionCache:
    """SQLite cache for derived alignment evidence, never raw document/source text."""

    def __init__(self, path: str | Path) -> None:
        settings = RevisionCacheSettings(path=str(path))
        self.connection = sqlite3.connect(settings.path)
        self.connection.execute("PRAGMA journal_mode = WAL")
        self.connection.execute("PRAGMA busy_timeout = 5000")
        self.connection.execute("PRAGMA synchronous = NORMAL")
        self.connection.execute("PRAGMA mmap_size = 268435456")
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS revision_evidence "
            "(chunk_hash TEXT PRIMARY KEY, payload TEXT NOT NULL)"
        )
        self.connection.commit()

    def put(self, result: RevisionEvidence) -> None:
        if not isinstance(result, RevisionEvidence):
            raise TypeError("result must be RevisionEvidence")
        payload = json.dumps([item.model_dump(mode="json") for item in result.evidence])
        self.connection.execute(
            "INSERT OR REPLACE INTO revision_evidence VALUES (?, ?)",
            (result.chunk_hash, payload),
        )
        self.connection.commit()

    def get(self, chunk_hash: str) -> RevisionEvidence | None:
        if not isinstance(chunk_hash, str) or len(chunk_hash) != 64:
            raise ValueError("chunk_hash must be a 64-character hash")
        row = self.connection.execute(
            "SELECT payload FROM revision_evidence WHERE chunk_hash = ?", (chunk_hash,)
        ).fetchone()
        if row is None:
            return None
        raw_evidence = json.loads(row[0])
        return RevisionEvidence(chunk_hash=chunk_hash, evidence=raw_evidence)

    def close(self) -> None:
        self.connection.close()
