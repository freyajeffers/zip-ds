import re

from zip_ds.queries.models import SearchCandidate

_TOKEN_PATTERN = re.compile(r"\b[\w']+\b", re.UNICODE)


def _trigrams(text: str) -> set[tuple[str, str, str]]:
    tokens = _TOKEN_PATTERN.findall(text.casefold())
    return set(zip(tokens, tokens[1:], tokens[2:]))


def snippet_jaccard(snippet: str, suspicious_text: str) -> float:
    """Return the Jaccard score over unique three-word shingles."""
    if not isinstance(snippet, str) or not isinstance(suspicious_text, str):
        raise TypeError("snippet and suspicious_text must be strings")
    snippet_grams = _trigrams(snippet)
    suspicious_grams = _trigrams(suspicious_text)
    if not snippet_grams and not suspicious_grams:
        return 0.0
    return len(snippet_grams & suspicious_grams) / len(snippet_grams | suspicious_grams)


def should_retrieve_candidate(
    candidate: SearchCandidate,
    suspicious_text: str,
    threshold: float = 0.20,
) -> bool:
    """Apply the snippet triage threshold before network retrieval."""
    if not isinstance(candidate, SearchCandidate):
        raise TypeError("candidate must be a SearchCandidate model")
    if not isinstance(threshold, float) or not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be a float between 0.0 and 1.0")
    return snippet_jaccard(candidate.snippet, suspicious_text) >= threshold
