import pytest

from zip_ds.retrieval.scraper import scrub_buffer


def test_scrub_buffer_overwrites_ephemeral_bytes():
    buffer = bytearray(b"sensitive source text")
    scrub_buffer(buffer)
    assert buffer == bytearray(len(buffer))


def test_scrub_buffer_rejects_immutable_or_non_buffer_values():
    with pytest.raises(TypeError):
        scrub_buffer(b"immutable")
