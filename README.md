# Zero-Ingestion Plagiarism Detection Service (ZIP-DS)

ZIP-DS is a privacy-oriented plagiarism-attribution project. The current checkout implements document ingestion, bounded query/provider plumbing, ephemeral retrieval, alignment, scoring/reporting, revision orchestration, and a small REST API.

## Current capabilities

- TXT, PDF, and DOCX extraction constrained to an authorized root directory.
- Pydantic v2 validation for document, style, extraction, query, cache, and search-candidate contracts.
- Unicode normalization and bibliography-section isolation.
- Document chunk hashing and query-sized chunk splitting.
- ASL, AWL, Yule's K, and function-word metrics; short texts bypass Yule's K.
- Bounded quoted-shingle query generation.
- Async provider boundary, provider failover/cooldown management, adaptive query stopping, token-bucket dispatch limiting, revision delta planning, lineage candidate suppression, and SQLite SERP metadata caching with WAL.
- A SerpAPI-compatible provider adapter parses organic results, maps HTTP 429 to provider failover, and keeps the API key runtime-only.
- `SerpApiProvider.as_client()` adapts provider searches to `ProviderManager` and `dispatch_queries`, preserving originating chunk IDs and failover behavior.
- `run_revision_scan()` connects cryptographic reuse, lineage candidate suppression, ephemeral retrieval, alignment, and reporting for unchanged revisions.
- Phase 3 snippet triage computes three-word-shingle Jaccard similarity and rejects low-overlap candidates before retrieval.
- Tier 1 lexical alignment finds exact contiguous matches and suppresses matches shorter than seven words.
- Tier 2 semantic alignment uses sentence-level token-set similarity with strict thresholds and character offsets; model-based embeddings are not required.
- Bounded asynchronous HTML retrieval stays in memory, strips script/style/navigation content, and skips network failures without aborting the scan.
- Structured scoring and Pydantic reporting contracts calculate evidence-weighted coverage and confidence while suppressing matches shorter than seven words.
- `run_scan()` integrates bounded in-memory alignment and structured reporting over already retrieved sources.
- `run_scan_from_candidates()` retrieves eligible candidates through the bounded ephemeral scraper before alignment and reporting.
- `run_scan_from_file()` enforces authorized-root extraction, normalization, bibliography isolation, ephemeral retrieval, alignment, and reporting for TXT, PDF, and DOCX inputs.
- `create_app(api_key=...)` optionally protects both endpoints with a runtime-only API key and constant-time comparison; report bodies are not persisted to disk.
- Cache persistence excludes candidate titles and snippets; fetched source bodies are not persisted.

## Setup

This project targets Python 3.14.8 and uses `uv`:

```bash
uv sync --extra dev
```

## Quality gates

Run all gates before committing source changes:

```bash
uv run ruff check .
uv run black --check .
uv run mypy zip_ds
uv run pytest -q
```

Coverage verification used by the repository audit:

```bash
uv run pytest -q --cov=zip_ds --cov-report=term-missing
```

## Public API

The supported package exports are defined in:

- `zip_ds`: document and style models
- `zip_ds.parsers`: extraction, sanitization, and typed `SecurityError` path-boundary exception
- `zip_ds.queries`: query generation, budgets, token-bucket limiting, cache, dispatch, and splitting
- `zip_ds.stylometry`: style-analysis functions

All public contracts use strict Pydantic v2 models where applicable. Extraction functions require both a file path and an authorized root:

```python
from zip_ds.parsers import read_txt

result = read_txt("input.txt", "/authorized/input-root")
```

## Project layout

- `zip_ds/models.py`: Pydantic document, style, and candidate contracts.
- `zip_ds/parsers/`: extraction and sanitization.
- `zip_ds/stylometry/`: intrinsic metrics.
- `zip_ds/queries/`: shingle generation, chunk splitting, budget, dispatch, and cache.
- `tests/`: unit, boundary, serialization, public-API, and cache tests.
- `docs/DEVELOPMENT.md`: dependency order and current development commands.
- `docs/INVARIANT_AUDIT.md`: current invariant audit and known phase gaps.
- `docs/ORIGINAL_DOCUMENTS.md`: index explaining the retained original project specifications.
- `AGENTS.md`: mandatory project invariants.

## Known limitations

The following specified components remain future phases: provider circuit-breakers and secondary-provider deployment configuration, multi-chunk revision persistence, CUSUM anomaly routing, embedding-based sentence-equivalent matching, explicit post-alignment memory scrubbing, HTML reports, authentication/authorization, systemd deployment, and benchmark suites.
