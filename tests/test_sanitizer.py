from zip_ds.parsers.sanitizer import isolate_bibliography, normalize_text


def test_normalize_text_removes_control_characters():
    result = normalize_text("A\x00B\u212B")
    assert result.text == "ABÅ"
    assert len(result.offsets) == len(result.text)


def test_isolate_bibliography():
    body, bibliography = isolate_bibliography("Essay body\n\nReferences\nSmith 2020")
    assert body == "Essay body"
    assert bibliography.startswith("References")


def test_isolate_bibliography_missing_heading():
    body, bibliography = isolate_bibliography("Essay body")
    assert body == "Essay body"
    assert bibliography == ""
