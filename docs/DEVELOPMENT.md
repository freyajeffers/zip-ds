# Development Guide

## Dependency order

1. Phase 1: parsers, sanitization, chunk contracts, and intrinsic stylometry.
2. Phase 2: query generation, budgeting, provider dispatch, and SERP caching.
3. Phase 3: ephemeral retrieval and lexical/semantic alignment.
4. Phase 4: scoring, report synthesis, and REST API.
5. Phase 5: systemd hardening and benchmark evaluation.

The current implementation is the Phase 1 foundation. Phase 2 must consume `DocumentChunk` objects rather than raw files; later phases must not bypass the path-validation and ephemeral-data boundaries.

## Local commands

```bash
uv sync
uv run pytest -q
uv run python -m zip_ds.cli scan sample_essay.pdf --output report.html
```

The CLI command is documented as the target interface in `README.md`; it is not implemented yet. Do not treat it as a passing command until `zip_ds.cli` exists.

## Phase 1 boundaries

- `zip_ds/parsers/document_extractor.py`: TXT, PDF, and DOCX extraction plus root confinement.
- `zip_ds/parsers/sanitizer.py`: Unicode normalization, control-character removal, and bibliography split.
- `zip_ds/models.py`: typed `DocumentChunk` and `StyleScores` contracts.
- `zip_ds/chunking.py`: deterministic SHA-256 chunk identity and offsets.
- `zip_ds/stylometry/analyzer.py`: ASL, AWL, Yule's K, function-word ratio, and short-text routing.

## Verification gates from the specification

- Reject traversal and symlink escapes.
- Preserve exact character offsets.
- Isolate References, Bibliography, and Works Cited sections.
- Bypass Yule's K and CUSUM for 50–300-word texts.
- Keep external source text ephemeral; no retrieval layer exists yet.
