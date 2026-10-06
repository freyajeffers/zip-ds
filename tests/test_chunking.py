from zip_ds.chunking import make_chunk


def test_make_chunk_tracks_offsets_and_hash():
    chunk = make_chunk("hello world", start_offset=4)
    assert chunk.end_offset == 15
    assert chunk.token_count == 2
    assert len(chunk.chunk_hash) == 64
    assert chunk.parent_chunk_id is None
