from collections.abc import Awaitable, Callable, Iterable

from pydantic import Field

from zip_ds.alignment import align_lexically, align_semantically
from zip_ds.chunking import make_chunk
from zip_ds.models import DocumentChunk, ValidatedModel
from zip_ds.parsers import extract_document, isolate_bibliography, normalize_text
from zip_ds.queries.models import SearchCandidate
from zip_ds.queries.reuse import RevisionEvidence, reuse_alignment_evidence
from zip_ds.queries.revision_cache import RevisionCache
from zip_ds.queries.revisions import suppress_lineage_candidates
from zip_ds.reporting import AlignmentEvidence, PlagiarismReport, build_report
from zip_ds.retrieval import EphemeralSource, retrieve_candidates


class ScanSource(ValidatedModel):
    url: str = Field(min_length=1)
    text: str = Field(min_length=1)


def _word_count(text: str) -> int:
    return len(text.split())


def run_scan(
    document_id: str,
    suspicious_text: str,
    sources: Iterable[ScanSource],
) -> PlagiarismReport:
    """Run bounded in-memory alignment and reporting over already retrieved sources."""
    if not isinstance(document_id, str) or not document_id:
        raise ValueError("document_id must be non-empty")
    if not isinstance(suspicious_text, str) or not suspicious_text.strip():
        raise ValueError("suspicious_text must be non-empty")
    chunk = make_chunk(suspicious_text)
    evidence: list[AlignmentEvidence] = []
    for source in sources:
        if not isinstance(source, ScanSource):
            raise TypeError("sources must contain ScanSource models")
        semantic_matches = align_semantically(
            chunk.raw_text, source.text, source.url, chunk.chunk_id
        )
        matches = semantic_matches or align_lexically(
            chunk.raw_text, source.text, source.url, chunk.chunk_id
        )
        evidence.extend(
            AlignmentEvidence(
                suspicious_chunk_id=match.suspicious_chunk_id,
                source_url=match.source_url,
                alignment_type=str(match.alignment_type),
                matched_word_count=_word_count(match.matched_susp_text),
                confidence_score=match.confidence_score,
            )
            for match in matches
        )
    return build_report(document_id, chunk.token_count, evidence)


async def run_revision_scan(
    document_id: str,
    suspicious_text: str,
    previous_chunks: Iterable[DocumentChunk],
    cached_results: Iterable[RevisionEvidence],
    candidates: list[SearchCandidate],
    *,
    cache: RevisionCache | None = None,
    excluded_lineage_urls: set[str] | None = None,
    retriever: Callable[
        [list[SearchCandidate], str], Awaitable[list[EphemeralSource]]
    ] = retrieve_candidates,
) -> PlagiarismReport:
    """Scan a revision while reusing unchanged evidence and excluding prior lineage URLs."""
    current_chunk = make_chunk(suspicious_text)
    previous = list(previous_chunks)
    previous_hashes = {chunk.chunk_hash for chunk in previous}
    eligible_cache = [result for result in cached_results if result.chunk_hash in previous_hashes]
    if cache is not None:
        for chunk_hash in previous_hashes:
            persisted = cache.get(chunk_hash)
            if persisted is not None and all(
                result.chunk_hash != persisted.chunk_hash for result in eligible_cache
            ):
                eligible_cache.append(persisted)
    reused, pending = reuse_alignment_evidence([current_chunk], eligible_cache)
    filtered_candidates = suppress_lineage_candidates(candidates, excluded_lineage_urls or set())
    evidence = list(reused)
    if pending:
        fresh = await run_scan_from_candidates(
            document_id, suspicious_text, filtered_candidates, retriever=retriever
        )
        evidence.extend(fresh.evidence)
        if cache is not None:
            cache.put(
                RevisionEvidence(chunk_hash=current_chunk.chunk_hash, evidence=fresh.evidence)
            )
    return build_report(document_id, current_chunk.token_count, evidence)


async def run_revision_scan_chunks(
    document_id: str,
    current_chunks: list[DocumentChunk],
    previous_chunks: Iterable[DocumentChunk],
    cached_results: Iterable[RevisionEvidence],
    candidates: list[SearchCandidate],
    *,
    cache: RevisionCache | None = None,
    excluded_lineage_urls: set[str] | None = None,
    retriever: Callable[
        [list[SearchCandidate], str], Awaitable[list[EphemeralSource]]
    ] = retrieve_candidates,
) -> PlagiarismReport:
    """Scan multiple chunks in a revision, reusing cached evidence and retrieving only for pending chunks.

    This function reads persisted derived evidence when available, rebinds cached
    evidence to the current chunk IDs, suppresses prior-lineage candidates, and
    performs a single batched retrieval for all pending chunks before aligning
    each pending chunk against the retrieved ephemeral sources.
    """
    if not isinstance(current_chunks, list) or not all(
        isinstance(c, DocumentChunk) for c in current_chunks
    ):
        raise TypeError("current_chunks must be a list of DocumentChunk models")
    previous = list(previous_chunks)
    previous_hashes = {chunk.chunk_hash for chunk in previous}

    # Gather eligible cached results from supplied cache blobs
    eligible_cache = [result for result in cached_results if result.chunk_hash in previous_hashes]
    if cache is not None:
        for chunk_hash in previous_hashes:
            persisted = cache.get(chunk_hash)
            if persisted is not None and all(
                r.chunk_hash != persisted.chunk_hash for r in eligible_cache
            ):
                eligible_cache.append(persisted)

    # Reuse evidence where possible; get pending chunks needing alignment
    reused, pending = reuse_alignment_evidence(current_chunks, eligible_cache)
    pending_ids = {c.chunk_id for c in pending}

    # Suppress prior-lineage candidates before retrieval
    filtered_candidates = suppress_lineage_candidates(candidates, excluded_lineage_urls or set())

    # Only retrieve candidates that belong to pending chunks
    candidates_for_pending = [
        c for c in filtered_candidates if c.originating_chunk_id in pending_ids
    ]

    evidence: list[AlignmentEvidence] = list(reused)

    if pending and candidates_for_pending:
        # Single batched retrieval for pending candidates
        retrieved = await retriever(
            candidates_for_pending, " ".join(c.raw_text for c in current_chunks)
        )
        # Map retrieved sources by URL for per-chunk alignment
        url_to_source = {s.source_url: s for s in retrieved}

        for chunk in pending:
            # find sources corresponding to this chunk's candidates
            urls = [
                c.url for c in candidates_for_pending if c.originating_chunk_id == chunk.chunk_id
            ]
            sources = [
                ScanSource(url=url, text=url_to_source[url].text)
                for url in urls
                if url in url_to_source
            ]
            if not sources:
                continue
            report = run_scan(document_id, chunk.raw_text, sources)
            evidence.extend(report.evidence)
            # persist derived evidence for this chunk
            if cache is not None:
                cache.put(RevisionEvidence(chunk_hash=chunk.chunk_hash, evidence=report.evidence))

    return build_report(document_id, sum(c.token_count for c in current_chunks), evidence)


async def run_scan_from_candidates(
    document_id: str,
    suspicious_text: str,
    candidates: list[SearchCandidate],
    retriever: Callable[
        [list[SearchCandidate], str], Awaitable[list[EphemeralSource]]
    ] = retrieve_candidates,
) -> PlagiarismReport:
    """Retrieve candidate pages ephemerally, then run alignment and reporting."""
    if not isinstance(candidates, list) or not all(
        isinstance(candidate, SearchCandidate) for candidate in candidates
    ):
        raise TypeError("candidates must be a list of SearchCandidate models")
    if not callable(retriever):
        raise TypeError("retriever must be callable")
    retrieved = await retriever(candidates, suspicious_text)
    if not isinstance(retrieved, list) or not all(
        isinstance(source, EphemeralSource) for source in retrieved
    ):
        raise TypeError("retriever must return a list of EphemeralSource models")
    sources = [ScanSource(url=source.source_url, text=source.text) for source in retrieved]
    return run_scan(document_id, suspicious_text, sources)


async def run_scan_from_file(
    document_id: str,
    path: str,
    authorized_root: str,
    candidates: list[SearchCandidate],
    retriever: Callable[
        [list[SearchCandidate], str], Awaitable[list[EphemeralSource]]
    ] = retrieve_candidates,
) -> PlagiarismReport:
    """Extract and sanitize a user document, then run the candidate pipeline."""
    extracted = extract_document(path, authorized_root)
    normalized = normalize_text(extracted.text)
    main_text, _bibliography = isolate_bibliography(normalized.text)
    return await run_scan_from_candidates(document_id, main_text, candidates, retriever=retriever)
