import re
from enum import StrEnum
from typing import Final
from urllib.parse import urlparse
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

_MIN_MATCH_WORDS: Final = 7
_TOKEN_PATTERN = re.compile(r"\b[\w']+\b", re.UNICODE)


class AlignmentType(StrEnum):
    VERBATIM = "verbatim"


class LexicalMatch(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    match_id: UUID = Field(default_factory=uuid4)
    suspicious_chunk_id: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    alignment_type: AlignmentType
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


Token = tuple[str, int, int]


def _tokens(text: str) -> list[Token]:
    return [
        (match.group(0).casefold(), match.start(), match.end())
        for match in _TOKEN_PATTERN.finditer(text)
    ]


def align_lexically(
    suspicious_text: str,
    source_text: str,
    source_url: str,
    suspicious_chunk_id: str,
) -> list[LexicalMatch]:
    if not all(
        isinstance(value, str)
        for value in (suspicious_text, source_text, source_url, suspicious_chunk_id)
    ):
        raise TypeError("alignment inputs must be strings")
    parsed_url = urlparse(source_url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValueError("source_url must be HTTP(S)")
    if not suspicious_chunk_id:
        raise ValueError("suspicious_chunk_id must be non-empty")
    suspicious_tokens = _tokens(suspicious_text)
    source_tokens = _tokens(source_text)
    if not suspicious_tokens or not source_tokens:
        return []

    previous = [0] * (len(source_tokens) + 1)
    best_length = 0
    best_suspicious_end = 0
    best_source_end = 0
    for suspicious_index, suspicious_token in enumerate(suspicious_tokens, start=1):
        current = [0] * (len(source_tokens) + 1)
        for source_index, source_token in enumerate(source_tokens, start=1):
            if suspicious_token[0] == source_token[0]:
                current[source_index] = previous[source_index - 1] + 1
                if current[source_index] > best_length:
                    best_length = current[source_index]
                    best_suspicious_end = suspicious_index
                    best_source_end = source_index
        previous = current

    if best_length < _MIN_MATCH_WORDS:
        return []
    suspicious_start = suspicious_tokens[best_suspicious_end - best_length][1]
    suspicious_end = suspicious_tokens[best_suspicious_end - 1][2]
    source_start = source_tokens[best_source_end - best_length][1]
    source_end = source_tokens[best_source_end - 1][2]
    return [
        LexicalMatch(
            suspicious_chunk_id=suspicious_chunk_id,
            source_url=source_url,
            alignment_type=AlignmentType.VERBATIM,
            susp_start_char=suspicious_start,
            susp_end_char=suspicious_end,
            matched_susp_text=suspicious_text[suspicious_start:suspicious_end],
            matched_source_text=source_text[source_start:source_end],
            confidence_score=1.0,
        )
    ]
