import pytest

from zip_ds.queries.generator import generate_queries, query_budget, shingles


def test_empty_and_short_inputs_do_not_create_partial_shingles():
    assert shingles("") == []
    assert shingles("one two") == []
    assert generate_queries("") == []


def test_shingles_normalize_case_and_punctuation():
    assert shingles("One, two! THREE four five six seven eight", size=6) == [
        '"one two three four five six"',
        '"two three four five six seven"',
        '"three four five six seven eight"',
    ]


def test_generate_queries_respects_explicit_limit():
    text = " ".join(f"word{i}" for i in range(30))
    assert len(generate_queries(text, max_queries=2)) == 2


@pytest.mark.parametrize(
    ("words", "expected"),
    [(0, 3), (1, 4), (374, 6), (375, 6), (1000, 11), (5249, 45), (10000, 45)],
)
def test_query_budget_boundaries(words: int, expected: int):
    assert query_budget(words) == expected
