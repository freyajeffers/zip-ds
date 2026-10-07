# Changelog

All notable changes to this project are recorded here.

## Unreleased

### Added

- Phase 1 parser foundation for TXT, PDF, and DOCX extraction with authorized-root path confinement.
- Unicode sanitization, bibliography isolation, document chunk hashing, and query-sized chunk splitting.
- Phase 1 stylometry metrics: average sentence length, average word length, Yule's K, and function-word ratio.
- Phase 2 bounded quoted-shingle query generation, query budgets, adaptive stopping, and SQLite WAL SERP metadata caching.
- Strict Pydantic v2 contracts for documents, extraction results, style scores, search candidates, query budgets, cache settings, cache entries, and normalized text.
- Explicit package APIs through `__all__` exports.
- Exhaustive boundary, serialization, cache, public-API, and parser tests.
- `docs/INVARIANT_AUDIT.md` documenting verified invariants and incomplete future phases.

### Changed

- Project targets Python 3.14.8 and uses `uv` for dependency resolution.
- Cache persistence excludes candidate titles and snippets to avoid persisting retrieved source plaintext.
- README now describes only implemented behavior and exact local quality-gate commands.

### Verification

- Ruff, Black, mypy, and pytest pass.
- Current test suite: 46 tests passed with 92% total coverage.

### Not yet implemented

- External provider clients, token-bucket rate limiting, circuit breakers, retrieval, alignment, scoring, reports, REST APIs, systemd deployment, revision lineage reuse, CUSUM routing, and benchmark suites.
