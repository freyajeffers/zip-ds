# Invariant Audit

Audit scope: tracked Python source, tests, packaging configuration, and project instructions in this repository. Generated caches and `.venv` were excluded.

## Verified

- Invariant 2: `run_scan_from_file` uses extension-dispatched extraction after canonical authorized-root validation; TXT/PDF/DOCX paths are covered, while symlink and malformed-document cases remain limited to extractor tests.
- Invariant 4: `SerpCache` configures WAL, `busy_timeout=5000`, `synchronous=NORMAL`, and `mmap_size=268435456`; pragma tests pass.
- Invariant 7: root, parser, query, and stylometry packages expose explicit `__all__` APIs; public API tests pass.
- Invariant 8: document, style, search, extraction, normalization, budget, cache settings, and cache entry contracts use strict Pydantic v2 models.
- Invariant 9: current implementation uses standard-library SQLite, hashing, URL parsing, asyncio protocols, and declared libraries for PDF, DOCX, validation, and formatting.
- Invariant 10: 105 tests cover valid, invalid, boundary, cache, serialization, API/authentication/provider-status/health, memory scrubbing, triage, lexical-alignment, semantic-alignment, scraper, limiter, provider-manager/status, SerpAPI parsing/dispatch, single- and multi-chunk revision reuse/cache/orchestration, scoring, reporting, pipeline, and document-dispatch cases.
- Invariant 11: current public boundaries validate paths, text, hashes, offsets, URLs, enums, scores, budgets, provider results, serialized cache payloads, snippet-triage inputs, lexical-alignment outputs, ephemeral-source outputs, and strict REST health/scan/report responses. `/health` emits no secret material.

## Partial or blocked by missing phases

- Invariant 1: revision evidence persistence stores only chunk hashes and derived alignment metadata in a WAL SQLite cache; raw document/source text is excluded by contract. Retrieval response bytearrays are overwritten after extraction, but Python immutable decoded strings cannot be deterministically scrubbed.
- Invariant 3: uncached query dispatch routes through a bounded token bucket, `ProviderManager` supports rate-limit cooldown/failover and exposes typed redacted status snapshots, and configured REST reports include those statuses; `SerpApiProvider` maps HTTP 429 to typed failover signals, while credentials and secondary-provider deployment remain external concerns.
- Invariant 5: `calculate_revision_delta` identifies unchanged chunk hashes, `reuse_alignment_evidence` rebinds cached evidence to current chunk IDs without provider queries, `RevisionCache` persists derived evidence, `run_revision_scan` and `run_revision_scan_chunks` read/write that cache and orchestrate single- and multi-chunk reuse/retrieval, and `suppress_lineage_candidates` removes prior-draft URLs.
- Invariant 6: short-text Yule's K bypass and six-token micro-shingles exist; Phase 3 has three-word-shingle snippet triage, seven-word lexical-match suppression, and sentence-level semantic approximation; CUSUM, anomaly routing, and embedding-based sentence equivalence are not implemented yet.
- Invariant 11: parser, query, retrieval, alignment, scoring, report, scan-pipeline, and REST request/response boundaries are validated; optional constant-time API-key protection is covered, while key provisioning and rotation remain deployment gaps.

## Quality gates

- `uv run ruff check .` — passed
- `uv run black --check .` — passed
- `uv run mypy zip_ds` — passed
- `uv run pytest -q --cov=zip_ds --cov-report=term-missing` — 105 passed, 91% total coverage
- `.github/workflows/quality.yml` runs the four quality gates on pushes to `main` and pull requests.

## Documentation and configuration findings

- Removed the stale `plaigarism` console-script entry because no `plaigarism:main` module exists.
- Added ignores for editor swap, backup, persistent-undo, and temporary files.
- Updated `docs/DEVELOPMENT.md` to remove the unimplemented CLI command and use the exact dev setup command.

## Remaining gaps

The implementation does not yet satisfy invariants that require future phases: external retrieval lifecycle, token-bucket limiting, provider circuit breakers, revision-lineage reuse, self-collusion suppression, CUSUM routing, seven-word match suppression, alignment, reporting, and REST boundaries.
