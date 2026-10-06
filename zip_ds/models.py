from enum import Enum
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator


class ValidatedModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True, strict=True)


class StyleScores(ValidatedModel):
    asl: float = Field(default=0.0, ge=0.0, allow_inf_nan=False)
    awl: float = Field(default=0.0, ge=0.0, allow_inf_nan=False)
    yules_k: float = Field(default=0.0, ge=0.0, allow_inf_nan=False)
    function_word_entropy: float = Field(default=0.0, ge=0.0, allow_inf_nan=False)
    anomaly_z_score: float = Field(default=0.0, ge=0.0, allow_inf_nan=False)


class DocumentChunk(ValidatedModel):
    chunk_id: str = Field(min_length=1)
    chunk_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    parent_chunk_id: str | None = None
    start_offset: int = Field(ge=0)
    end_offset: int = Field(ge=0)
    raw_text: str
    token_count: int = Field(ge=0)
    is_bibliography: bool = False
    stylometric_scores: StyleScores = Field(default_factory=StyleScores)
    is_anomalous: bool = False

    @field_validator("end_offset")
    @classmethod
    def end_after_start(cls, value: int, info: ValidationInfo) -> int:
        start = info.data.get("start_offset", 0)
        if value < start:
            raise ValueError("end_offset must not precede start_offset")
        return value

    @model_validator(mode="after")
    def validate_offsets_and_tokens(self) -> DocumentChunk:
        if self.end_offset - self.start_offset != len(self.raw_text):
            raise ValueError("offsets must span raw_text")
        if self.token_count != len(self.raw_text.split()):
            raise ValueError("token_count must match raw_text")
        return self


class SourceType(str, Enum):
    WEB = "web"
    ACADEMIC_PAPER = "academic_paper"
    REPOSITORY = "repository"


class SearchCandidate(ValidatedModel):
    url: str
    source_type: SourceType
    title: str = Field(min_length=1)
    snippet: str = Field(min_length=1)
    rank_position: int = Field(ge=1)
    matched_query: str = Field(min_length=1)
    originating_chunk_id: str = Field(min_length=1)
    snippet_jaccard_score: float = Field(default=0.0, ge=0.0, le=1.0)

    @field_validator("url")
    @classmethod
    def require_http_url(cls, value: str) -> str:
        if urlparse(value).scheme not in {"http", "https"} or not urlparse(value).netloc:
            raise ValueError("candidate URL must be HTTP(S)")
        return value
