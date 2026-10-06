import math
import re
from collections import Counter

from zip_ds.models import StyleScores

_FUNCTION_WORDS = {
    "a", "an", "and", "as", "at", "but", "by", "for", "from", "in", "of", "on", "or", "the", "to", "with", "is", "are", "was", "were", "it", "this", "that"
}


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text.lower())


def average_sentence_length(text: str) -> float:
    words = _words(text)
    sentences = max(1, len(re.findall(r"[.!?]+", text)))
    return len(words) / sentences


def average_word_length(text: str) -> float:
    words = _words(text)
    return sum(map(len, words)) / len(words) if words else 0.0


def yules_k(text: str) -> float:
    words = _words(text)
    if not words:
        return 0.0
    frequencies = Counter(words)
    n = len(words)
    m1 = n
    m2 = sum(freq * freq for freq in frequencies.values())
    return 10_000 * (m2 - m1) / (m1 * m1)


def function_word_ratio(text: str) -> float:
    words = _words(text)
    return sum(word in _FUNCTION_WORDS for word in words) / len(words) if words else 0.0


def analyze(text: str) -> StyleScores:
    words = _words(text)
    # Short texts bypass unstable Yule/CUSUM statistics per Phase 1 routing.
    yule = 0.0 if len(words) <= 300 else yules_k(text)
    return StyleScores(
        asl=average_sentence_length(text),
        awl=average_word_length(text),
        yules_k=yule,
        function_word_entropy=function_word_ratio(text),
        anomaly_z_score=0.0,
    )
