from collections.abc import Awaitable, Callable, Iterable

from pydantic import Field

from zip_ds.alignment import align_lexically, align_semantically
from zip_ds.chunking import make_chunk
from zip_ds.models import ValidatedModel
from zip_ds.parsers import extract_document, isolate_bibliography, normalize_text
from zip_ds.queries.models import SearchCandidate
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
