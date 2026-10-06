from zip_ds.chunking import make_chunk
from zip_ds.models import DocumentChunk


def split_chunk_for_queries(chunk: DocumentChunk) -> list[DocumentChunk]:
    if len(chunk.raw_text) <= 3000:
        return [chunk]

    parts: list[DocumentChunk] = []
    start = 0
    text = chunk.raw_text
    while start < len(text):
        remaining = len(text) - start
        if remaining <= 3000:
            end = len(text)
        else:
            target = start + 3000
            boundary = text.rfind("\n", start + 800, target + 1)
            end = boundary + 1 if boundary >= start + 800 else target
        part_text = text[start:end]
        parts.append(
            make_chunk(
                part_text,
                start_offset=chunk.start_offset + start,
                parent_chunk_id=chunk.chunk_id,
                is_bibliography=chunk.is_bibliography,
            )
        )
        start = end
    return parts
