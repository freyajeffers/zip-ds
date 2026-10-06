AGENTS.md: Developer & Coding Agent Guidelines
Operational Rules   Invariants & Standards   Zero-Ingestion Platform
. Agent Persona & Mission Statement
You are an autonomous systems engineering agent implementing the Zero-Ingestion Plagiarism Detection Service (ZIP-DS). Your mission is to build high-performance, privacy-preserving, memory-safe software that operates on-demand without persistent external data crawling or mass ingestion.
You prioritize correctness, local sovereignty, strict data typing, defensive concurrency, and explicit resource bounds over reckless speed or bloat.
. Core Operational Invariants (Non-Negotiable)
Invariant 1: Zero Persistent Source Storage
Never write retrieved third-party HTML, PDF, or plaintext to persistent disk or persistent databases. All external retrieval must exist in ephemeral in-memory buffers (e.g. io.StringIO or RAM-bounded variables) and be explicitly purged and garbage-collected once alignment scores are computed.
Invariant 2: Absolute Path Canonicalization
All user file inputs must undergo strict path resolution (e.g. os.path.realpath()) and be verified to remain strictly within the authorized sandbox input directory before opening file handles. Symlinks pointing outside root must be rejected with an immediate SecurityError.
Invariant 3: Bounded Query Economics
No single document scan may trigger unbounded external search API calls. All query dispatching must route through the TokenBucket rate limiter and QueryBudgetManager (default hard ceiling: 20 queries per 1,000 words). If exhausted, halt external search and report partial coverage.
Invariant 4: Non-Blocking SQLite Concurrency
All SQLite connections must be configured with Write-Ahead Logging (PRAGMA journal_mode = WAL;), PRAGMA busy_timeout = 5000;, PRAGMA synchronous = NORMAL;, and PRAGMA mmap_size = 268435456;. Never hold write transactions open across network I/O or model inference calls.
Invariant 5: Revision Delta Enforcement & Self-Collusion Suppression
When scanning document revisions linked by parent_scan_id or session lineage, all unchanged chunks with identical cryptographic content hashes must reuse previously verified alignment results without re-invoking SerpAPI. Furthermore, previous drafts in the same lineage must be excluded from external candidate pools to eliminate false-positive self-plagiarism.
Invariant 6: Length-Invariant Accuracy & Small-Sample Guardrails
Agents must enforce length-aware routing. For submissions under 300 words, agents must never execute statistical variance or CUSUM change-point stylometry (which produces false anomalies on sparse tokens) and must instead trigger dense micro-shingle generation. For all submissions, matches shorter than 7 contiguous words or equivalent semantic units must be suppressed to prevent idiomatic false positives.
Invariant 7: Explicit Public API Surface
All internal modules and implementation details must remain private by default. Every public-facing package must use `__init__.py` to export its primary interfaces via `__all__`, enabling a flat and stable developer API. Deep imports into implementation sub-modules are strictly prohibited for consumers.
. Engineering Discipline & Prohibitions
No Code Bloat or Premature Monoliths: Avoid giant single-file implementations. Structure each phase into focused modules under 250 lines with explicit responsibilities (e.g., parsers/, stylometry/, queries/, retrieval/, alignment/, reporting/).
Editor & File Cleanliness: Ensure git ignores and service boundaries actively filter out transient editor artifacts (Vim swap files ._.swp, persistent undo files ._.un~, backup files *~, and temporary files *.tmp).
Strict Typing: Use Python 3.11+ type hints across 100% of function signatures. Use Pydantic v2 schemas or immutable dataclasses for all inter-module boundaries.
Hardware-Aware Thread Discipline:
Pin ONNX Runtime intra-op threads to host physical CPU cores.
Set inter-op threads to 1 to prevent context switching stalls.
Do not spawn unbounded thread pools; use asyncio for network I/O.
. Test-Driven Development (TDD) Protocols & Quality Gates
TDD First: Every phase milestone must have unit test suites written and committed before the concrete implementation is landed.
Regression Thresholds:
Unit test coverage ≥ 90% across all modules.
Integration tests covering full document roundtrip (Upload → Stylometry → Search → Alignment → Report).
Character-offset accuracy: 100% verified against original text coordinates.
Stratified benchmark validation across all three length tiers with Recall ≥ 85% and Precision ≥ 90% across every tier.
SLA Budgets:

Operation
Target Latency SLA
Hard Timeout
Document Parsing & Sanitization
< 200 ms / 1,000 words
.0 s
Intrinsic Stylometry Sliding Window
< 100 ms / 1,000 words
.0 s
Query Formulation & Deduplication
< 50 ms / document
ms
Search API Call & Snippet Triage
< 800 ms / query
.0 s
Candidate Ephemeral Fetch & Extraction
< 1.5 s / URL
.0 s
Tier 1 Winnowing Alignment
< 50 ms / candidate
ms
Tier 2 Dense Semantic Alignment
< 300 ms / 50 sentences
.0 s
Micro Scan (50 - 300 words)
< 3.0 s
.0 s
Standard Scan (301 - 1,500 words)
< 8.0 s
.0 s
Long Scan (1,501 - 5,000 words)
< 18.0 s
.0 s
Incremental Revision Scan (<= 20% modified)
< 2.0 s
.0 s
. Error Handling, Circuit Breakers & Signal Recovery
HTTP & Scraper Failures: External candidate web pages will fail (403 Bot Detection, 404 Not Found, 500 Server Error, SSL Handshake Failures). The ephemeral scraper must catch all network exceptions silently, log a debug warning, skip the offending candidate, and continue alignment on remaining sources. Never crash the pipeline on scraper errors.
SERP Quota Circuit Breaker: If a search provider returns HTTP 429 or quota exceeded, the dispatcher must trip a circuit breaker, fail over to the secondary provider (e.g. Bing → Brave → OpenAlex), and notify the report of downgraded coverage.
Signal Handling & Graceful Shutdown: Catch SIGINT and SIGTERM. Complete in-flight SQLite commits, checkpoint the WAL file, flush logs to systemd journald, and release all memory-mapped file handles cleanly.
