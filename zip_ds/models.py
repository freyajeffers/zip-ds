from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StyleScores:
    asl: float = 0.0
    awl: float = 0.0
    yules_k: float = 0.0
    function_word_entropy: float = 0.0
    anomaly_z_score: float = 0.0


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    chunk_hash: str
    parent_chunk_id: Optional[str]
    start_offset: int
    end_offset: int
    raw_text: str
    token_count: int
    is_bibliography: bool = False
    stylometric_scores: StyleScores = StyleScores()
    is_anomalous: bool = False
