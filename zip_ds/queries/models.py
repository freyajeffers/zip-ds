from dataclasses import dataclass
from enum import Enum


class SourceType(str, Enum):
    WEB = "web"
    ACADEMIC_PAPER = "academic_paper"
    REPOSITORY = "repository"


@dataclass(frozen=True)
class SearchCandidate:
    url: str
    source_type: SourceType
    title: str
    snippet: str
    rank_position: int
    matched_query: str
    originating_chunk_id: str
    snippet_jaccard_score: float = 0.0
