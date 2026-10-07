# Master Phased Implementation Plan

------------------------------------------------------------------------

Engineering Roadmap   Architecture & Delivery   5-Phase Pipeline

## 1. Executive Overview & Phase Sequencing

------------------------------------------------------------------------

This Master Implementation Plan details the phased construction of the
Zero-Ingestion Plagiarism Detection Service. The system is engineered to
deliver high-precision plagiarism attribution without the liability,
expense, or complexity of maintaining an ingested web crawler index.

The project is strictly decomposed into five sequential,
dependency-ordered phases. Each phase establishes clean module
boundaries, strict typed data contracts, automated unit and integration
tests, and quantitative verification gates before unlocking subsequent
phases.

## 2. Cross-Phase Dependency Graph

------------------------------------------------------------------------

┌────────────────────────────────────────────────────────┐\
│ Phase 1: Ingestion, Sanitization & Intrinsic Analysis  │\
└───────────────────────────┬────────────────────────────┘\
                           │ (Outputs Sanitized Chunks & Stylometric
Risk Flags)\
                           ▼\
┌────────────────────────────────────────────────────────┐\
│ Phase 2: Query Formulation & Search Dispatcher         │\
└───────────────────────────┬────────────────────────────┘\
                           │ (Outputs Ranked Candidate URLs & Search
Snippets)\
                           ▼\
┌────────────────────────────────────────────────────────┐\
│ Phase 3: Ephemeral Scraping & Dual-Tier Alignment      │\
└───────────────────────────┬────────────────────────────┘\
                           │ (Outputs Aligned Character Spans & Semantic
Scores)\
                           ▼\
┌────────────────────────────────────────────────────────┐\
│ Phase 4: Scoring Engine, Report Synthesis & REST API   │\
└───────────────────────────┬────────────────────────────┘\
                           │ (Outputs End-to-End Submission Pipeline &
Reports)\
                           ▼\
┌────────────────────────────────────────────────────────┐\
│ Phase 5: Hardening, Systemd Daemonization & PAN Bench  │\
└────────────────────────────────────────────────────────┘\

## 3. Phase Summaries & Deliverables

------------------------------------------------------------------------

Phase

Core Focus

Primary Deliverables

Blocking Exit Gate

 

Phase 1

Ingestion & Intrinsic Stylometry

- Document parsers (PDF, DOCX, TXT) with path traversal hardening.
- Length-Aware Ingestion Routing (Micro, Standard, Long regimes).
- Boilerplate and bibliography extraction/stripping.
- Paragraph segmentation & character-offset tracking.
- Stylometric extractor: ASL, AWL, Yule's K, function words.
- CUSUM change-point outlier detection algorithm.
- Differential chunk hashing (BLAKE3/SHA-256) and document lineage
  tracking.
- Boilerplate and bibliography extraction/stripping.
- Paragraph segmentation & character-offset tracking.
- Stylometric extractor: ASL, AWL, Yule's K, function words.
- CUSUM change-point outlier detection algorithm.
- Differential chunk hashing (BLAKE3/SHA-256) and document lineage
  tracking.

Clean text extraction across 100 sample documents; 100% of bibliography
sections isolated; \>95% unit test coverage on stylometry.

Phase 2

Query Formulation & Search Dispatcher

- Query-chunk provenance splitter (max 3,000 chars, min 800 chars).
- Length-Proportional Query Budgeting and Distributed Spatial Probing
  across 5,000 words.
- POS tagger and low-DF keyword filter (TF-IDF / YAKE).
- Quoted 8-word shingle generator & boolean term synthesizer.
- Multi-provider search client (Google/Bing/Brave + OpenAlex).
- SQLite WAL SERP cache with 7-day TTL and rate-limiting token bucket.
- Delta query formulation (only querying modified chunks) and
  self-plagiarism suppression across drafts.
- POS tagger and low-DF keyword filter (TF-IDF / YAKE).
- Quoted 8-word shingle generator & boolean term synthesizer.
- Multi-provider search client (Google/Bing/Brave + OpenAlex).
- SQLite WAL SERP cache with 7-day TTL and rate-limiting token bucket.
- Delta query formulation (only querying modified chunks) and
  self-plagiarism suppression across drafts.

Average query count ≤ 15 queries per 1,000 words; candidate recall \>
85% on standard test set; zero unhandled API rate limits.

Phase 3

Ephemeral Retrieval & Dual-Tier Alignment

- In-memory async scraper using Trafilatura and Readability.
- Snippet Jaccard pre-filter (τ = 0.20) to prevent useless fetches.
- Tier 1: Winnowing rolling hash & Smith-Waterman local alignment.
- Tier 2: FastEmbed / ONNX Runtime sentence embeddings (BGE-small).
- Cosine similarity chunk aligner with cross-encoder verification.

End-to-end memory purge confirmed (0 leaked HTML files); Tier 1 speed \<
50ms per candidate; Tier 2 semantic detection F1 \> 0.88.

Phase 4

Scoring, Reporting & REST API

- Overall similarity index calculator (de-duplicating overlapping
  spans).
- Length-Calibrated Scoring and Minimum-Length Collocation Filtering.
- Interactive side-by-side HTML comparison report with live URLs.
- FastAPI submission endpoint (POST /v1/scan, GET /v1/reports/{id}).
- Pydantic data models for input requests and scan results.
- Revision evolution reports (comparing Draft N to Draft N+1, showing
  resolved vs unresolved matches) and multi-draft lineage tracking.
- Interactive side-by-side HTML comparison report with live URLs.
- FastAPI submission endpoint (POST /v1/scan, GET /v1/reports/{id}).
- Pydantic data models for input requests and scan results.
- Revision evolution reports (comparing Draft N to Draft N+1, showing
  resolved vs unresolved matches) and multi-draft lineage tracking.

API latency SLA \< 15s for 2,000-word documents; valid OpenAPI 3.1
specification; full character-offset integrity verified.

Phase 5

Hardening, Daemonization & PAN Benchmark

- Systemd user service (zip-ds.service) and maintenance timer.
- Systemd sandbox directives (ProtectSystem=strict, PrivateTmp=true).
- PAN CLEF benchmark evaluation runner (MRR, nDCG@10, Recall@10) across
  stratified length buckets (50-300 words, 301-1,500 words, 1,501-5,000
  words).
- Automated log rotation, WAL checkpointing, and clean teardown.
- Systemd sandbox directives (ProtectSystem=strict, PrivateTmp=true).
- PAN CLEF benchmark evaluation runner (MRR, nDCG@10, Recall@10).
- Automated log rotation, WAL checkpointing, and clean teardown.

Zero regression against PAN benchmark baseline; automated service
recovery under simulated crash; 0 memory leaks under 100 concurrent
scans.

## 4. Operational Invariants & Definition of Done

------------------------------------------------------------------------

- Zero Persistent Storage Invariant: At no point in the lifecycle of any
  scan may retrieved third-party HTML, PDF, or full-text content be
  written to persistent disk storage. All scraping, alignment, and
  scoring must occur strictly in RAM buffers and be purged on
  completion.
- Deterministic Offset Guarantee: Character offsets reported in the
  final attribution report must map back exactly to the original
  uploaded document coordinates, irrespective of formatting conversions.
- Strict Search Quota Budgets: Every document has an enforced hard
  ceiling on external search queries (default: 25 queries per 1,000
  words). If the budget is exhausted, the search engine halts gracefully
  and reports partial coverage rather than blowing past cost limits.
- Revision Delta Invariant: When a submission provides a parent_scan_id
  or matches an existing revision tree, unchanged chunks with identical
  cryptographic content hashes must reuse existing alignment results
  with zero redundant SerpAPI calls.
- Length-Invariant Accuracy Guarantee: System performance must exhibit
  zero degradation across the entire 50 to 5,000 word spectrum,
  maintaining Recall \>= 85% and Precision \>= 90% in all length tiers
  through adaptive routing, dense micro-shingles for short text, and
  distributed spatial probing for long text.
