import os

from zip_ds.parsers.document_extractor import canonicalize_and_validate, read_txt

TEST_DIR = os.path.dirname(__file__)


def test_read_txt(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("hello world")
    text, chunks = read_txt(str(p))
    assert "hello world" in text
    assert chunks[0][1] == len(text)


def test_canonicalize_and_validate(tmp_path):
    root = str(tmp_path)
    p = tmp_path / "subdir"
    p.mkdir()
    f = p / "file.txt"
    f.write_text("x")
    real = canonicalize_and_validate(str(f), root)
    assert real.startswith(root)


def test_canonicalize_rejects_sibling_prefix(tmp_path):
    import pytest

    root = tmp_path / "allowed"
    sibling = tmp_path / "allowed-escape"
    root.mkdir()
    sibling.mkdir()
    with pytest.raises(ValueError):
        canonicalize_and_validate(str(sibling / "x.txt"), str(root))
