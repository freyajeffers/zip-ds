import pytest

from zip_ds.pipeline import run_scan, run_scan_from_candidates
from zip_ds.queries.models import SearchCandidate, SourceType
from zip_ds.retrieval.scraper import EphemeralSource


def candidate() -> SearchCandidate:
    return SearchCandidate(
        url="https://example.com/source",
        source_type=SourceType.WEB,
        rank_position=1,
        matched_query="cat garden",
        originating_chunk_id="chunk-1",
        snippet_jaccard_score=0.8,
    )


def test_run_scan_from_candidates_retrieves_ephemeral_sources():
    async def fake_retriever(
        candidates: list[SearchCandidate], suspicious_text: str
    ) -> list[EphemeralSource]:
        assert candidates == [candidate()]
        return [
            EphemeralSource(
                source_url=candidates[0].url,
                text="Before sunrise, the cat crossed the quiet garden quickly.",
            )
        ]

    report = __import__("asyncio").run(
        run_scan_from_candidates(
            "doc-1",
            "The cat quickly crossed the quiet garden before sunrise.",
            [candidate()],
            retriever=fake_retriever,
        )
    )

    assert report.score.evidence_count == 1


def test_run_scan_rejects_non_source_items():
    with pytest.raises(TypeError):
        run_scan("doc-1", "valid text", ["not-a-source"])  # type: ignore[list-item]
