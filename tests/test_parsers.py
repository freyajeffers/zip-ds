import os

import pytest

from zip_ds.parsers.document_extractor import (
    ExtractionResult,
    SecurityError,
    canonicalize_and_validate,
    read_txt,
)

TEST_DIR = os.path.dirname(__file__)


def test_read_txt_validates_root_and_returns_pydantic_output(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("hello world")
    result = read_txt(str(p), str(tmp_path))
    assert isinstance(result, ExtractionResult)
    assert result.text == "hello world"
    assert result.offsets[0] == (0, len(result.text))


def test_read_txt_rejects_outside_root(tmp_path):
    root = tmp_path / "allowed"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret")
    with pytest.raises(SecurityError):
        read_txt(str(outside), str(root))


def test_canonicalize_and_validate(tmp_path):
    root = str(tmp_path)
    p = tmp_path / "subdir"
    p.mkdir()
    f = p / "file.txt"
    f.write_text("x")
    real = canonicalize_and_validate(str(f), root)
    assert real.startswith(root)


def test_canonicalize_rejects_sibling_prefix(tmp_path):
    root = tmp_path / "allowed"
    sibling = tmp_path / "allowed-escape"
    root.mkdir()
    sibling.mkdir()
    with pytest.raises(SecurityError):
        canonicalize_and_validate(str(sibling / "x.txt"), str(root))
