import re


def _require_text(text: str) -> None:
    if not isinstance(text, str):
        raise TypeError("text must be a string")


def _tokens(text: str) -> list[str]:
    _require_text(text)
    return re.findall(r"[A-Za-z0-9]+", text.lower())


def shingles(text: str, size: int = 8, step: int = 1) -> list[str]:
    if not isinstance(size, int) or size < 1:
        raise ValueError("size must be a positive integer")
    if not isinstance(step, int) or step < 1:
        raise ValueError("step must be a positive integer")
    tokens = _tokens(text)
    return [
        '"' + " ".join(tokens[i : i + size]) + '"'
        for i in range(0, max(0, len(tokens) - size + 1), step)
    ]


def query_budget(word_count: int) -> int:
    if not isinstance(word_count, int) or word_count < 0:
        raise ValueError("word_count must be a non-negative integer")
    return max(3, min(45, int(3 + 0.008 * word_count + 0.999999)))


def generate_queries(text: str, max_queries: int | None = None) -> list[str]:
    _require_text(text)
    if max_queries is not None and (not isinstance(max_queries, int) or max_queries < 0):
        raise ValueError("max_queries must be None or a non-negative integer")
    size = 6 if len(_tokens(text)) <= 300 else 8
    step = 2 if size == 6 else 1
    queries = shingles(text, size=size, step=step)
    limit = max_queries if max_queries is not None else query_budget(len(_tokens(text)))
    return queries[:limit]
