import re


def _tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text.lower())


def shingles(text: str, size: int = 8, step: int = 1) -> list[str]:
    tokens = _tokens(text)
    return ["\"" + " ".join(tokens[i : i + size]) + "\"" for i in range(0, max(0, len(tokens) - size + 1), step)]


def query_budget(word_count: int) -> int:
    return max(3, min(45, int(3 + 0.008 * word_count + 0.999999)))


def generate_queries(text: str, max_queries: int | None = None) -> list[str]:
    size = 6 if len(_tokens(text)) <= 300 else 8
    step = 2 if size == 6 else 1
    queries = shingles(text, size=size, step=step)
    limit = max_queries if max_queries is not None else query_budget(len(_tokens(text)))
    return queries[:limit]
