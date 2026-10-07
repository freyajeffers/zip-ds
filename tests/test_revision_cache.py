import pytest

from zip_ds.queries.reuse import RevisionEvidence
from zip_ds.queries.revision_cache import RevisionCache, RevisionCacheSettings
from zip_ds.reporting.scoring import AlignmentEvidence


def item() -> RevisionEvidence:
    return RevisionEvidence(
        chunk_hash="a" * 64,
        evidence=[
            AlignmentEvidence(
                suspicious_chunk_id="chunk-1",
                source_url="https://example.com/source",
                alignment_type="verbatim",
                matched_word_count=8,
                confidence_score=1.0,
            )
        ],
    )


def test_revision_cache_round_trips_derived_evidence_only(tmp_path):
    cache = RevisionCache(tmp_path / "revision.db")
    cache.put(item())

    restored = cache.get("a" * 64)

    assert restored == item()
    columns = cache.connection.execute("PRAGMA table_info(revision_evidence)").fetchall()
    assert [column[1] for column in columns] == ["chunk_hash", "payload"]
    cache.close()


def test_revision_cache_configures_required_pragmas(tmp_path):
    cache = RevisionCache(tmp_path / "revision.db")
    assert cache.connection.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    assert cache.connection.execute("PRAGMA busy_timeout").fetchone()[0] == 5000
    assert cache.connection.execute("PRAGMA synchronous").fetchone()[0] == 1
    assert cache.connection.execute("PRAGMA mmap_size").fetchone()[0] == 268435456
    cache.close()


def test_revision_cache_rejects_invalid_settings():
    with pytest.raises(ValueError):
        RevisionCacheSettings(path="")
