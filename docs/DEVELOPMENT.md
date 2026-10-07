# Development Guide

## Dependency order

1. Phase 1: parsers, sanitization, chunk contracts, and intrinsic stylometry.
2. Phase 2: query generation, budgeting, provider dispatch, and SERP caching.
3. Phase 3: ephemeral retrieval and lexical/semantic alignment.
4. Phase 4: scoring, report synthesis, and REST API.
5. Phase 5: systemd hardening and benchmark evaluation.

The current implementation includes the Phase 1 foundation and Phase 2 query/budget/cache scaffolding. Phase 2 consumes generated query strings; later phases must not bypass the path-validation and ephemeral-data boundaries.

## Local commands

```bash
uv sync --extra dev
uv run ruff check .
uv run black --check .
uv run mypy zip_ds
uv run pytest -q
```

Coverage audit command:

```bash
uv run pytest -q --cov=zip_ds --cov-report=term-missing
```

There is no implemented CLI or REST scan command in this checkout. Do not document or invoke `zip_ds.cli` until that module exists.

## Phase 1 boundaries

- `zip_ds/parsers/document_extractor.py`: TXT, PDF, and DOCX extraction plus root confinement.
- `zip_ds/parsers/sanitizer.py`: Unicode normalization, control-character removal, and bibliography split.
- `zip_ds/models.py`: typed `DocumentChunk` and `StyleScores` contracts.
- `zip_ds/chunking.py`: deterministic SHA-256 chunk identity and offsets.
- `zip_ds/stylometry/analyzer.py`: ASL, AWL, Yule's K, function-word ratio, and short-text routing.
- `zip_ds/retrieval/triage.py`: three-word-shingle Jaccard gate before candidate retrieval.
- `zip_ds/queries/limiter.py`: token-bucket rate limiting for uncached provider dispatch.
- `zip_ds/queries/providers.py`: provider manager with rate-limit cooldown and secondary-provider failover.
- `zip_ds/queries/serpapi.py`: runtime-key SerpAPI-compatible provider adapter and typed organic-result parsing.
- `SerpApiProvider.as_client()` adapts chunk-aware provider calls to the generic `ProviderClient`/`ProviderManager`/`dispatch_queries` path.
- `zip_ds/queries/revisions.py`: cryptographic revision delta partitioning and lineage candidate suppression.
- `zip_ds/alignment/lexical.py`: exact contiguous lexical matches with seven-word suppression.
- `zip_ds/alignment/semantic.py`: sentence-level token-set semantic approximation with strict thresholds and offsets.
- `zip_ds/reporting/scoring.py`: evidence-weighted coverage and confidence calculation with seven-word suppression.
- `zip_ds/reporting/report.py`: strict structured plagiarism report contract.
- `zip_ds/parsers/document.py`: extension-dispatched authorized TXT/PDF/DOCX extraction.
- `zip_ds/pipeline.py`: bounded in-memory scan orchestration from suspicious text and retrieved sources to a typed report, plus candidate retrieval and document-file integration.
- `zip_ds/retrieval/scraper.py`: bounded in-memory HTML extraction and failure-tolerant async retrieval.

## Verification gates from the specification

- Reject traversal and symlink escapes.
- Preserve exact character offsets.
- Isolate References, Bibliography, and Works Cited sections.
- Bypass Yule's K and CUSUM for 50–300-word texts.
- Keep external source text ephemeral; HTML retrieval exists, but PDF retrieval and post-alignment scrubbing do not yet exist.

CI runs the same four quality gates on pushes to `main` and all pull requests via `.github/workflows/quality.yml`.
