# Invariant Audit

Audit scope: tracked Python source, tests, packaging configuration, and project instructions in this repository. Generated caches and `.venv` were excluded.

## Verified

- Invariant 2: document extraction now requires an authorized root, uses canonical path confinement, and raises typed `SecurityError` for escapes; sibling-prefix and outside-root tests pass.
- Invariant 4: `SerpCache` configures WAL, `busy_timeout=5000`, `synchronous=NORMAL`, and `mmap_size=268435456`; pragma tests pass.
- Invariant 7: root, parser, query, and stylometry packages expose explicit `__all__` APIs; public API tests pass.
- Invariant 8: document, style, search, extraction, normalization, budget, cache settings, and cache entry contracts use strict Pydantic v2 models.
- Invariant 9: current implementation uses standard-library SQLite, hashing, URL parsing, asyncio protocols, and declared libraries for PDF, DOCX, validation, and formatting.
- Invariant 10: 67 tests cover valid, invalid, boundary, cache, serialization, API, triage, lexical-alignment, scraper, limiter, and provider-manager cases.
- Invariant 11: current public boundaries validate paths, text, hashes, offsets, URLs, enums, scores, budgets, provider results, serialized cache payloads, snippet-triage inputs, lexical-alignment outputs, and ephemeral-source outputs.

## Partial or blocked by missing phases

- Invariant 1: HTML retrieval uses bounded in-memory buffers and persists no fetched source text; explicit post-alignment scrubbing and PDF retrieval remain incomplete. The SERP cache persists only query strings and candidate URLs, not titles, snippets, or source bodies.
- Invariant 3: uncached query dispatch routes through a bounded token bucket, and `ProviderManager` supports rate-limit cooldown/failover; concrete external providers and downgraded-coverage reporting are not implemented yet.
- Invariant 5: revision lineage, unchanged-chunk reuse, and self-plagiarism exclusion are not implemented yet.
- Invariant 6: short-text Yule's K bypass and six-token micro-shingles exist; Phase 3 has three-word-shingle snippet triage and seven-word lexical-match suppression; CUSUM, anomaly routing, and semantic sentence-equivalent suppression are not implemented yet.
- Invariant 11: the current Phase 2 and Phase 3 triage/lexical-alignment boundaries are validated, but future retrieval, semantic alignment, reporting, and REST boundaries do not exist yet and therefore cannot be validated.

## Quality gates

- `uv run ruff check .` — passed
- `uv run black --check .` — passed
- `uv run mypy zip_ds` — passed
- `uv run pytest -q --cov=zip_ds --cov-report=term-missing` — 61 passed, 91% total coverage
- `.github/workflows/quality.yml` runs the four quality gates on pushes to `main` and pull requests.

## Documentation and configuration findings

- Removed the stale `plaigarism` console-script entry because no `plaigarism:main` module exists.
- Added ignores for editor swap, backup, persistent-undo, and temporary files.
- Updated `docs/DEVELOPMENT.md` to remove the unimplemented CLI command and use the exact dev setup command.

## Remaining gaps

The implementation does not yet satisfy invariants that require future phases: external retrieval lifecycle, token-bucket limiting, provider circuit breakers, revision-lineage reuse, self-collusion suppression, CUSUM routing, seven-word match suppression, alignment, reporting, and REST boundaries.
