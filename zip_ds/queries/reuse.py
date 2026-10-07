from collections.abc import Iterable

from pydantic import Field

from zip_ds.models import DocumentChunk, ValidatedModel
from zip_ds.reporting.scoring import AlignmentEvidence


class RevisionEvidence(ValidatedModel):
    """In-memory alignment results keyed by immutable chunk hash."""

    chunk_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    evidence: list[AlignmentEvidence]


def reuse_alignment_evidence(
    current_chunks: Iterable[DocumentChunk],
    cached_results: Iterable[RevisionEvidence],
) -> tuple[list[AlignmentEvidence], list[DocumentChunk]]:
    """Reuse prior alignment evidence for unchanged chunks without external queries."""
    cache: dict[str, list[AlignmentEvidence]] = {}
    for result in cached_results:
        if result.chunk_hash in cache:
            raise ValueError("cached revision evidence contains duplicate hashes")
        cache[result.chunk_hash] = result.evidence

    reused: list[AlignmentEvidence] = []
    pending: list[DocumentChunk] = []
    seen_hashes: set[str] = set()
    for chunk in current_chunks:
        if chunk.chunk_hash in seen_hashes:
            raise ValueError("current revision contains duplicate chunk hashes")
        seen_hashes.add(chunk.chunk_hash)
        prior = cache.get(chunk.chunk_hash)
        if prior is None:
            pending.append(chunk)
            continue
        reused.extend(
            item.model_copy(update={"suspicious_chunk_id": chunk.chunk_id}) for item in prior
        )
    return reused, pending
