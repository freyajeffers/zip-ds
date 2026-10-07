from collections.abc import Iterable

from pydantic import Field

from zip_ds.alignment import align_lexically, align_semantically
from zip_ds.chunking import make_chunk
from zip_ds.models import ValidatedModel
from zip_ds.reporting import AlignmentEvidence, PlagiarismReport, build_report


class ScanSource(ValidatedModel):
    url: str = Field(min_length=1)
    text: str = Field(min_length=1)


def _word_count(text: str) -> int:
    return len(text.split())


def run_scan(
    document_id: str,
    suspicious_text: str,
    sources: Iterable[ScanSource],
) -> PlagiarismReport:
    """Run bounded in-memory alignment and reporting over already retrieved sources."""
    if not isinstance(document_id, str) or not document_id:
        raise ValueError("document_id must be non-empty")
    if not isinstance(suspicious_text, str) or not suspicious_text.strip():
        raise ValueError("suspicious_text must be non-empty")
    chunk = make_chunk(suspicious_text)
    evidence: list[AlignmentEvidence] = []
    for source in sources:
        if not isinstance(source, ScanSource):
            raise TypeError("sources must contain ScanSource models")
        semantic_matches = align_semantically(
            chunk.raw_text, source.text, source.url, chunk.chunk_id
        )
        matches = semantic_matches or align_lexically(
            chunk.raw_text, source.text, source.url, chunk.chunk_id
        )
        evidence.extend(
            AlignmentEvidence(
                suspicious_chunk_id=match.suspicious_chunk_id,
                source_url=match.source_url,
                alignment_type=str(match.alignment_type),
                matched_word_count=_word_count(match.matched_susp_text),
                confidence_score=match.confidence_score,
            )
            for match in matches
        )
    return build_report(document_id, chunk.token_count, evidence)
