import hashlib
import uuid

from zip_ds.models import DocumentChunk


def make_chunk(
    text: str,
    start_offset: int = 0,
    parent_chunk_id: str | None = None,
    is_bibliography: bool = False,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=str(uuid.uuid4()),
        chunk_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        parent_chunk_id=parent_chunk_id,
        start_offset=start_offset,
        end_offset=start_offset + len(text),
        raw_text=text,
        token_count=len(text.split()),
        is_bibliography=is_bibliography,
    )
