from collections.abc import Iterable
from uuid import UUID, uuid4

from pydantic import Field

from zip_ds.models import ValidatedModel
from zip_ds.reporting.scoring import AlignmentEvidence, ScoreResult, calculate_score


class PlagiarismReport(ValidatedModel):
    report_id: UUID = Field(default_factory=uuid4)
    document_id: str = Field(min_length=1)
    score: ScoreResult
    evidence: list[AlignmentEvidence] = Field(default_factory=list)


def build_report(
    document_id: str,
    total_suspicious_words: int,
    evidence: Iterable[AlignmentEvidence],
) -> PlagiarismReport:
    if not isinstance(document_id, str) or not document_id:
        raise ValueError("document_id must be non-empty")
    items = list(evidence)
    return PlagiarismReport(
        document_id=document_id,
        score=calculate_score(items, total_suspicious_words),
        evidence=items,
    )
