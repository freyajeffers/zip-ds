import re
from enum import StrEnum
from typing import Final
from urllib.parse import urlparse
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

_MIN_SEMANTIC_WORDS: Final = 7
_SENTENCE_PATTERN = re.compile(r"[^.!?]+[.!?]?(?:\s+|$)", re.UNICODE)
_TOKEN_PATTERN = re.compile(r"\b[\w']+\b", re.UNICODE)


class SemanticAlignmentType(StrEnum):
    SEMANTIC = "semantic"


class SemanticMatch(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    match_id: UUID = Field(default_factory=uuid4)
    suspicious_chunk_id: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    alignment_type: SemanticAlignmentType = SemanticAlignmentType.SEMANTIC
    susp_start_char: int = Field(ge=0)
    susp_end_char: int = Field(ge=0)
    matched_susp_text: str = Field(min_length=1)
    matched_source_text: str = Field(min_length=1)
    confidence_score: float = Field(ge=0.0, le=1.0)

    @field_validator("source_url")
    @classmethod
    def require_http_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("source_url must be HTTP(S)")
        return value


def _sentences(text: str) -> list[tuple[str, int, int]]:
    return [
        (match.group(0).strip(), match.start(), match.end())
        for match in _SENTENCE_PATTERN.finditer(text)
        if match.group(0).strip()
    ]


def _words(text: str) -> set[str]:
    return {match.group(0).casefold() for match in _TOKEN_PATTERN.finditer(text)}


def align_semantically(
    suspicious_text: str,
    source_text: str,
    source_url: str,
    suspicious_chunk_id: str,
    threshold: float = 0.75,
) -> list[SemanticMatch]:
    if not all(
        isinstance(value, str)
        for value in (suspicious_text, source_text, source_url, suspicious_chunk_id)
    ):
        raise TypeError("alignment inputs must be strings")
    if not isinstance(threshold, float) or not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be a float between 0.0 and 1.0")
    parsed_url = urlparse(source_url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValueError("source_url must be HTTP(S)")
    if not suspicious_chunk_id:
        raise ValueError("suspicious_chunk_id must be non-empty")

    source_sentences = _sentences(source_text)
    matches: list[SemanticMatch] = []
    for suspicious_sentence, start, end in _sentences(suspicious_text):
        suspicious_words = _words(suspicious_sentence)
        if len(suspicious_words) < _MIN_SEMANTIC_WORDS:
            continue
        best: tuple[float, str] | None = None
        for source_sentence, _, _ in source_sentences:
            source_words = _words(source_sentence)
            union = suspicious_words | source_words
            score = len(suspicious_words & source_words) / len(union) if union else 0.0
            if best is None or score > best[0]:
                best = (score, source_sentence)
        if best is not None and best[0] >= threshold:
            matches.append(
                SemanticMatch(
                    suspicious_chunk_id=suspicious_chunk_id,
                    source_url=source_url,
                    susp_start_char=start,
                    susp_end_char=end,
                    matched_susp_text=suspicious_sentence,
                    matched_source_text=best[1],
                    confidence_score=best[0],
                )
            )
    return matches
