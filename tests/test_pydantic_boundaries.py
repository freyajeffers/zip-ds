import pytest
from pydantic import ValidationError

from zip_ds.parsers.sanitizer import NormalizedText
from zip_ds.queries.dispatcher import QueryBudget


def test_normalized_text_validates_offset_output_shape():
    result = NormalizedText(text="abc", offsets=[(0, 1), (1, 2), (2, 3)])
    assert result.text == "abc"
    with pytest.raises(ValidationError):
        NormalizedText(text="abc", offsets=[(0, 1)])
    with pytest.raises(ValidationError):
        NormalizedText(text="abc", offsets=[(1, 0), (1, 2), (2, 3)])


def test_query_budget_is_a_validated_pydantic_state_model():
    budget = QueryBudget(word_count=100, maximum=1)
    assert budget.limit == 1
    budget.consume()
    assert budget.used == 1
    with pytest.raises(ValidationError):
        QueryBudget(word_count=-1)
    with pytest.raises(ValidationError):
        QueryBudget(word_count=100, maximum=-1)
