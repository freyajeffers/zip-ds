from zip_ds.queries.generator import generate_queries, query_budget


def test_short_queries_use_dense_six_word_shingles():
    text = "one two three four five six seven eight nine ten"
    queries = generate_queries(text)
    assert queries[0] == '"one two three four five six"'
    assert len(queries) == 3


def test_query_budget_is_bounded():
    assert query_budget(1000) == 11
    assert query_budget(10000) == 45
