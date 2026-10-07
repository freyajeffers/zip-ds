# Zero-Ingestion Plagiarism Detection Service (ZIP-DS)

ZIP-DS is a privacy-oriented plagiarism-attribution project. The current checkout implements the Phase 1 ingestion foundation, Phase 2 query-generation/cache scaffolding, and the Phase 3 snippet-triage gate. It does not yet implement external provider clients, source retrieval, alignment, scoring, reporting, or a REST/CLI scan pipeline.

## Current capabilities

- TXT, PDF, and DOCX extraction constrained to an authorized root directory.
- Pydantic v2 validation for document, style, extraction, query, cache, and search-candidate contracts.
- Unicode normalization and bibliography-section isolation.
- Document chunk hashing and query-sized chunk splitting.
- ASL, AWL, Yule's K, and function-word metrics; short texts bypass Yule's K.
- Bounded quoted-shingle query generation.
- Async provider boundary, adaptive query stopping, and SQLite SERP metadata caching with WAL.
- Phase 3 snippet triage computes three-word-shingle Jaccard similarity and rejects low-overlap candidates before retrieval.
- Tier 1 lexical alignment finds exact contiguous matches and suppresses matches shorter than seven words.
- Cache persistence excludes candidate titles and snippets; fetched source bodies are not implemented or persisted.

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
- `zip_ds.queries`: query generation, budgets, cache, dispatch, and splitting
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
- `docs/DEVELOPMENT.md`: dependency order and development commands.
- `docs/INVARIANT_AUDIT.md`: current invariant audit and known phase gaps.
- `AGENTS.md`: mandatory project invariants.

## Known limitations

The following specified components remain future phases: token-bucket provider rate limiting, circuit breakers, revision-lineage reuse, self-plagiarism suppression, CUSUM anomaly routing, semantic sentence-equivalent matching, external retrieval, dense semantic alignment, scoring, HTML reports, REST APIs, systemd deployment, and benchmark suites.
