from pathlib import Path

import pytest

from zip_ds.parsers.document import extract_document


def test_extract_document_dispatches_txt(tmp_path: Path):
    path = tmp_path / "submission.txt"
    path.write_text("alpha beta", encoding="utf-8")

    result = extract_document(str(path), str(tmp_path))

    assert result.text == "alpha beta"
    assert result.offsets == [(0, len(result.text))]


def test_extract_document_rejects_unknown_extension(tmp_path: Path):
    path = tmp_path / "submission.md"
    path.write_text("alpha", encoding="utf-8")

    with pytest.raises(ValueError, match="unsupported document"):
        extract_document(str(path), str(tmp_path))
