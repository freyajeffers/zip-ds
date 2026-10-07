from collections.abc import Iterable

from pydantic import Field

from zip_ds.models import DocumentChunk, SearchCandidate, ValidatedModel


class RevisionDelta(ValidatedModel):
    """Chunks requiring new work and chunks eligible for result reuse."""

    unchanged_chunk_ids: list[str] = Field(default_factory=list)
    modified_chunks: list[DocumentChunk] = Field(default_factory=list)


def calculate_revision_delta(
    current_chunks: Iterable[DocumentChunk],
    previous_chunks: Iterable[DocumentChunk],
) -> RevisionDelta:
    """Partition current chunks by cryptographic identity against a prior revision."""
    current = list(current_chunks)
    previous_hashes = {chunk.chunk_hash for chunk in previous_chunks}
    seen_hashes: set[str] = set()
    unchanged: list[str] = []
    modified: list[DocumentChunk] = []
    for chunk in current:
        if chunk.chunk_hash in seen_hashes:
            raise ValueError("current revision contains duplicate chunk hashes")
        seen_hashes.add(chunk.chunk_hash)
        if chunk.chunk_hash in previous_hashes:
            unchanged.append(chunk.chunk_id)
        else:
            modified.append(chunk)
    return RevisionDelta(unchanged_chunk_ids=unchanged, modified_chunks=modified)


def suppress_lineage_candidates(
    candidates: Iterable[SearchCandidate],
    excluded_urls: set[str],
) -> list[SearchCandidate]:
    """Remove candidates belonging to prior drafts in the same revision lineage."""
    if not isinstance(excluded_urls, set):
        raise TypeError("excluded_urls must be a set")
    return [candidate for candidate in candidates if candidate.url not in excluded_urls]
