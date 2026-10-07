# Changelog

All notable changes to this project are recorded here.

## Unreleased

### Added

- Phase 1 parser foundation for TXT, PDF, and DOCX extraction with authorized-root path confinement.
- Unicode sanitization, bibliography isolation, document chunk hashing, and query-sized chunk splitting.
- Phase 1 stylometry metrics: average sentence length, average word length, Yule's K, and function-word ratio.
- Phase 2 bounded quoted-shingle query generation, query budgets, adaptive stopping, and SQLite WAL SERP metadata caching.
- Phase 3 snippet triage computes three-word-shingle Jaccard similarity and rejects low-overlap candidates before retrieval.
- Tier 1 lexical alignment finds exact contiguous matches and suppresses matches shorter than seven words.
- Token-bucket query limiting is applied to uncached provider dispatches.
- Provider manager failover and cooldown handling for rate-limited providers.
- Sentence-level semantic-alignment approximation with minimum-length suppression and strict confidence thresholds.
- Evidence-weighted scoring and structured Pydantic plagiarism reports with coverage/confidence fields.
- Candidate retrieval is integrated into the bounded scan pipeline through the ephemeral scraper.
- SerpAPI adapter is now wired through `ProviderManager` into cached, rate-limited query dispatch; provider clocks use monotonic time without requiring an active event loop.
- Authorized-root TXT/PDF/DOCX extraction and document-to-report pipeline integration.
- Strict Pydantic v2 contracts for documents, extraction results, style scores, search candidates, query budgets, cache settings, cache entries, and normalized text.
- Typed `SecurityError` is raised for paths escaping an authorized extraction root.
- Explicit package APIs through `__all__` exports.
- Exhaustive boundary, serialization, cache, public-API, and parser tests.
- `docs/INVARIANT_AUDIT.md` documenting verified invariants and incomplete future phases.

### Changed

- Project targets Python 3.14.8 and uses `uv` for dependency resolution.
- Cache persistence excludes candidate titles and snippets to avoid persisting retrieved source plaintext.
- README now describes only implemented behavior and exact local quality-gate commands.
- CI runs the same quality gates for pushes to `main` and pull requests.
- Removed the stale console-script entry because no CLI module exists.
- Added `docs/ORIGINAL_DOCUMENTS.md` to distinguish retained source specifications from current implementation documentation.
- Retained the original project-creation and development documents under `docs/` as design references.

### Verification

- Ruff, Black, mypy, and pytest pass.
- Current test suite: 88 tests passed with 89% total coverage.

### Not yet implemented

- External provider clients, secondary-provider circuit-breaker failover, PDF retrieval, semantic alignment, scoring, reports, REST APIs, systemd deployment, revision lineage reuse, CUSUM routing, and benchmark suites.
