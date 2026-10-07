from collections.abc import Iterable

from pydantic import Field

from zip_ds.models import ValidatedModel

_MIN_MATCH_WORDS = 7


class AlignmentEvidence(ValidatedModel):
    suspicious_chunk_id: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    alignment_type: str = Field(min_length=1)
    matched_word_count: int = Field(ge=1)
    confidence_score: float = Field(ge=0.0, le=1.0)


class ScoreResult(ValidatedModel):
    matched_word_count: int = Field(ge=0)
    evidence_count: int = Field(ge=0)
    coverage_score: float = Field(ge=0.0, le=1.0)
    confidence_score: float = Field(ge=0.0, le=1.0)


def calculate_score(
    evidence: Iterable[AlignmentEvidence], total_suspicious_words: int
) -> ScoreResult:
    if not isinstance(total_suspicious_words, int) or total_suspicious_words < 1:
        raise ValueError("total_suspicious_words must be a positive integer")
    qualifying = [item for item in evidence if item.matched_word_count >= _MIN_MATCH_WORDS]
    matched_words = min(total_suspicious_words, sum(item.matched_word_count for item in qualifying))
    confidence = (
        sum(item.matched_word_count * item.confidence_score for item in qualifying)
        / sum(item.matched_word_count for item in qualifying)
        if qualifying
        else 0.0
    )
    return ScoreResult(
        matched_word_count=matched_words,
        evidence_count=len(qualifying),
        coverage_score=matched_words / total_suspicious_words,
        confidence_score=confidence,
    )
