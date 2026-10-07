# Invariant Audit

Audit scope: tracked Python source, tests, packaging configuration, and project instructions in this repository. Generated caches and `.venv` were excluded.

## Verified

- Invariant 2: document extraction now requires an authorized root, uses canonical path confinement, and raises typed `SecurityError` for escapes; sibling-prefix and outside-root tests pass.
- Invariant 4: `SerpCache` configures WAL, `busy_timeout=5000`, `synchronous=NORMAL`, and `mmap_size=268435456`; pragma tests pass.
- Invariant 7: root, parser, query, and stylometry packages expose explicit `__all__` APIs; public API tests pass.
- Invariant 8: document, style, search, extraction, normalization, budget, cache settings, and cache entry contracts use strict Pydantic v2 models.
- Invariant 9: current implementation uses standard-library SQLite, hashing, URL parsing, asyncio protocols, and declared libraries for PDF, DOCX, validation, and formatting.
- Invariant 10: 46 tests cover valid, invalid, boundary, cache, serialization, and API cases.
- Invariant 11: current public boundaries validate paths, text, hashes, offsets, URLs, enums, scores, budgets, provider results, and serialized cache payloads.

## Partial or blocked by missing phases

- Invariant 1: the SERP cache no longer persists candidate titles or snippets, but it does persist query strings and candidate URLs. Query strings are derived from user input; URLs are metadata, not fetched source text. Any future retrieval layer must never persist fetched HTML, PDF, or plaintext.
- Invariant 3: query-count budgeting exists, but a token-bucket limiter and concurrent provider backoff/circuit breaker are not implemented yet.
- Invariant 5: revision lineage, unchanged-chunk reuse, and self-plagiarism exclusion are not implemented yet.
- Invariant 6: short-text Yule's K bypass and six-token micro-shingles exist; CUSUM, anomaly routing, and the seven-word match suppression rule are not implemented yet.
- Invariant 11: the current Phase 2 boundary is validated, but future retrieval, alignment, reporting, and REST boundaries do not exist yet and therefore cannot be validated.

## Quality gates

- `uv run ruff check .` — passed
- `uv run black --check .` — passed
- `uv run mypy zip_ds` — passed
- `uv run pytest -q --cov=zip_ds --cov-report=term-missing` — 46 passed, 92% total coverage
- `.github/workflows/quality.yml` runs the four quality gates on pushes to `main` and pull requests.

## Documentation and configuration findings

- Removed the stale `plaigarism` console-script entry because no `plaigarism:main` module exists.
- Added ignores for editor swap, backup, persistent-undo, and temporary files.
- Updated `docs/DEVELOPMENT.md` to remove the unimplemented CLI command and use the exact dev setup command.

## Remaining gaps

The implementation does not yet satisfy invariants that require future phases: external retrieval lifecycle, token-bucket limiting, provider circuit breakers, revision-lineage reuse, self-collusion suppression, CUSUM routing, seven-word match suppression, alignment, reporting, and REST boundaries.
