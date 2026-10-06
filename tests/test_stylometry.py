from zip_ds.stylometry.analyzer import analyze, average_sentence_length, average_word_length, yules_k


def test_basic_style_metrics():
    text = "This is a short sentence. Another short sentence."
    assert average_sentence_length(text) == 4.0
    assert average_word_length(text) > 0
    assert yules_k(text) >= 0


def test_short_text_bypasses_yule():
    scores = analyze("one two three four five")
    assert scores.yules_k == 0.0
    assert scores.function_word_entropy == 0.0
