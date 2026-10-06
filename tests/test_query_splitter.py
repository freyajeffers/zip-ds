from zip_ds.models import DocumentChunk
from zip_ds.queries.splitter import split_chunk_for_queries


def make_chunk(text: str) -> DocumentChunk:
    return DocumentChunk(
        chunk_id="id",
        chunk_hash="0" * 64,
        parent_chunk_id=None,
        start_offset=100,
        end_offset=100 + len(text),
        raw_text=text,
        token_count=len(text.split()),
    )


def test_short_chunk_is_returned_unchanged():
    chunk = make_chunk("x" * 799)
    parts = split_chunk_for_queries(chunk)
    assert [part.raw_text for part in parts] == [chunk.raw_text]
    assert parts[0].start_offset == 100


def test_long_chunk_is_partitioned_with_bounded_parts_and_offsets():
    text = "a" * 800 + "\n" + "b" * 800 + "\n" + "c" * 800
    parts = split_chunk_for_queries(make_chunk(text))
    assert len(parts) == 1  # 2,402 characters stays below the 3,000-character maximum

    longer = "a" * 1500 + "\n" + "b" * 1500 + "\n" + "c" * 1500
    parts = split_chunk_for_queries(make_chunk(longer))
    assert len(parts) >= 2
    assert all(800 <= len(part.raw_text) <= 3000 for part in parts)
    assert parts[0].start_offset == 100
    assert parts[-1].end_offset == 100 + len(longer)


def test_bibliography_flag_is_preserved():
    chunk = make_chunk("x" * 3200)
    chunk = DocumentChunk(**{**chunk.__dict__, "is_bibliography": True})
    assert all(part.is_bibliography for part in split_chunk_for_queries(chunk))
