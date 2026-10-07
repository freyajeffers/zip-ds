from zip_ds.models import DocumentChunk
from zip_ds.queries.reuse import RevisionEvidence, reuse_alignment_evidence
from zip_ds.reporting.scoring import AlignmentEvidence


def chunk(chunk_id: str, digest: str) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        chunk_hash=digest,
        start_offset=0,
        end_offset=5,
        raw_text="alpha",
        token_count=1,
    )


def evidence() -> AlignmentEvidence:
    return AlignmentEvidence(
        suspicious_chunk_id="old",
        source_url="https://example.com/source",
        alignment_type="verbatim",
        matched_word_count=8,
        confidence_score=1.0,
    )


def test_reuse_alignment_evidence_by_cryptographic_hash():
    digest = "a" * 64
    cache = [RevisionEvidence(chunk_hash=digest, evidence=[evidence()])]

    reused, pending = reuse_alignment_evidence(
        [chunk("new-id", digest), chunk("changed", "b" * 64)], cache
    )

    assert reused[0].suspicious_chunk_id == "new-id"
    assert pending[0].chunk_id == "changed"
