from pathlib import Path

import pytest

from zip_ds.pipeline import run_scan_from_file
from zip_ds.queries.models import SearchCandidate, SourceType
from zip_ds.retrieval.scraper import EphemeralSource


def test_run_scan_from_file_normalizes_and_retrieves(tmp_path: Path):
    path = tmp_path / "submission.txt"
    path.write_text("The cat quickly crossed the quiet garden before sunrise.", encoding="utf-8")
    candidate = SearchCandidate(
        url="https://example.com/source",
        source_type=SourceType.WEB,
        rank_position=1,
        matched_query="cat garden",
        originating_chunk_id="chunk-1",
        snippet_jaccard_score=0.8,
    )

    async def fake_retriever(candidates: list[SearchCandidate], text: str):
        assert text.startswith("The cat")
        return [
            EphemeralSource(
                source_url=candidates[0].url,
                text="Before sunrise, the cat crossed the quiet garden quickly.",
            )
        ]

    report = __import__("asyncio").run(
        run_scan_from_file("doc-1", str(path), str(tmp_path), [candidate], retriever=fake_retriever)
    )

    assert report.score.evidence_count == 1


def test_run_scan_from_file_rejects_escape(tmp_path: Path):
    outside = tmp_path.parent / "outside.txt"
    outside.write_text("secret", encoding="utf-8")
    with pytest.raises(ValueError):
        __import__("asyncio").run(run_scan_from_file("doc-1", str(outside), str(tmp_path), []))
