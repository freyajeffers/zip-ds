from zip_ds.alignment.semantic import SemanticMatch, align_semantically


def test_semantic_alignment_returns_sentence_match_with_offsets():
    suspicious = "The cat quickly crossed the quiet garden before sunrise."
    source = "Before sunrise, the cat crossed the quiet garden quickly."

    matches = align_semantically(suspicious, source, "https://example.com/source", "chunk-1")

    assert len(matches) == 1
    assert isinstance(matches[0], SemanticMatch)
    assert matches[0].susp_start_char == 0
    assert matches[0].susp_end_char == len(suspicious)
    assert matches[0].confidence_score >= 0.75


def test_semantic_alignment_suppresses_short_sentences():
    matches = align_semantically(
        "A very short phrase.",
        "A very short phrase.",
        "https://example.com/source",
        "chunk-1",
    )

    assert matches == []


def test_semantic_alignment_rejects_invalid_threshold():
    try:
        align_semantically("alpha beta gamma", "alpha beta gamma", "https://example.com", "x", 1.1)
    except ValueError as error:
        assert "threshold" in str(error)
    else:
        raise AssertionError("expected threshold validation")
