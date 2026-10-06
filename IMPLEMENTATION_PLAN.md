1|Master Phased Implementation Plan
2|Engineering Roadmap   Architecture & Delivery   5-Phase Pipeline
3|1. Executive Overview & Phase Sequencing
4|This Master Implementation Plan details the phased construction of the Zero-Ingestion Plagiarism Detection Service. The system is engineered to deliver high-precision plagiarism attribution without the liability, expense, or complexity of maintaining an ingested web crawler index.
5|The project is strictly decomposed into five sequential, dependency-ordered phases. Each phase establishes clean module boundaries, strict typed data contracts, automated unit and integration tests, and quantitative verification gates before unlocking subsequent phases.
6|2. Cross-Phase Dependency Graph
7|┌────────────────────────────────────────────────────────┐
8|│ Phase 1: Ingestion, Sanitization & Intrinsic Analysis │
9|└───────────────────────────┬────────────────────────────┘
│ (Outputs Sanitized Chunks & Stylometric Risk Flags)
▼
12|┌────────────────────────────────────────────────────────┐
13|│ Phase 2: Query Formulation & Search Dispatcher │
14|└───────────────────────────┬────────────────────────────┘
│ (Outputs Ranked Candidate URLs & Search Snippets)
▼
17|┌────────────────────────────────────────────────────────┐
18|│ Phase 3: Ephemeral Scraping & Dual-Tier Alignment │
19|└───────────────────────────┬────────────────────────────┘
│ (Outputs Aligned Character Spans & Semantic Scores)
▼
22|┌────────────────────────────────────────────────────────┐
23|│ Phase 4: Scoring Engine, Report Synthesis & REST API │
24|└───────────────────────────┬────────────────────────────┘
│ (Outputs End-to-End Submission Pipeline & Reports)
▼
27|┌────────────────────────────────────────────────────────┐
28|│ Phase 5: Hardening, Systemd Daemonization & PAN Bench │
29|└────────────────────────────────────────────────────────┘
30|
31|3. Phase Summaries & Deliverables
32|
33|
34|Phase
35|Core Focus
36|Primary Deliverables
37|Blocking Exit Gate

39|Phase 1
40|Ingestion & Intrinsic Stylometry
41|Document parsers (PDF, DOCX, TXT) with path traversal hardening.
42|Length-Aware Ingestion Routing (Micro, Standard, Long regimes).
43|Boilerplate and bibliography extraction/stripping.
44|Paragraph segmentation & character-offset tracking.
45|Stylometric extractor: ASL, AWL, Yule's K, function words.
46|CUSUM change-point outlier detection algorithm.
47|Differential chunk hashing (BLAKE3/SHA-256) and document lineage tracking.
48|Boilerplate and bibliography extraction/stripping.
49|Paragraph segmentation & character-offset tracking.
50|Stylometric extractor: ASL, AWL, Yule's K, function words.
51|CUSUM change-point outlier detection algorithm.
52|Differential chunk hashing (BLAKE3/SHA-256) and document lineage tracking.
53|Clean text extraction across 100 sample documents; 100% of bibliography sections isolated; >95% unit test coverage on stylometry.
54|Phase 2
55|Query Formulation & Search Dispatcher
56|Query-chunk provenance splitter (max 3,000 chars, min 800 chars).
57|Length-Proportional Query Budgeting and Distributed Spatial Probing across 5,000 words.
58|POS tagger and low-DF keyword filter (TF-IDF / YAKE).
59|Quoted 8-word shingle generator & boolean term synthesizer.
60|Multi-provider search client (Google/Bing/Brave + OpenAlex).
61|SQLite WAL SERP cache with 7-day TTL and rate-limiting token bucket.
62|Delta query formulation (only querying modified chunks) and self-plagiarism suppression across drafts.
63|POS tagger and low-DF keyword filter (TF-IDF / YAKE).
64|Quoted 8-word shingle generator & boolean term synthesizer.
65|Multi-provider search client (Google/Bing/Brave + OpenAlex).
66|SQLite WAL SERP cache with 7-day TTL and rate-limiting token bucket.
67|Delta query formulation (only querying modified chunks) and self-plagiarism suppression across drafts.
68|Average query count ≤ 15 queries per 1,000 words; candidate recall > 85% on standard test set; zero unhandled API rate limits.
69|Phase 3
70|Ephemeral Retrieval & Dual-Tier Alignment
71|In-memory async scraper using Trafilatura and Readability.
72|Snippet Jaccard pre-filter (τ = 0.20) to prevent useless fetches.
73|Tier 1: Winnowing rolling hash & Smith-Waterman local alignment.
74|Tier 2: FastEmbed / ONNX Runtime sentence embeddings (BGE-small).
75|Cosine similarity chunk aligner with cross-encoder verification.
76|End-to-end memory purge confirmed (0 leaked HTML files); Tier 1 speed < 50ms per candidate; Tier 2 semantic detection F1 > 0.88.
77|Phase 4
78|Scoring, Reporting & REST API
79|Overall similarity index calculator (de-duplicating overlapping spans).
80|Length-Calibrated Scoring and Minimum-Length Collocation Filtering.
81|Interactive side-by-side HTML comparison report with live URLs.
82|FastAPI submission endpoint (POST /v1/scan, GET /v1/reports/{id}).
83|Pydantic data models for input requests and scan results.
84|Revision evolution reports (comparing Draft N to Draft N+1, showing resolved vs unresolved matches) and multi-draft lineage tracking.
85|Interactive side-by-side HTML comparison report with live URLs.
86|FastAPI submission endpoint (POST /v1/scan, GET /v1/reports/{id}).
87|Pydantic data models for input requests and scan results.
88|Revision evolution reports (comparing Draft N to Draft N+1, showing resolved vs unresolved matches) and multi-draft lineage tracking.
89|API latency SLA < 15s for 2,000-word documents; valid OpenAPI 3.1 specification; full character-offset integrity verified.
90|Phase 5
91|Hardening, Daemonization & PAN Benchmark
92|Systemd user service (zip-ds.service) and maintenance timer.
93|Systemd sandbox directives (ProtectSystem=strict, PrivateTmp=true).
94|PAN CLEF benchmark evaluation runner (MRR, nDCG@10, Recall@10) across stratified length buckets (50-300 words, 301-1,500 words, 1,501-5,000 words).
95|Automated log rotation, WAL checkpointing, and clean teardown.
96|Systemd sandbox directives (ProtectSystem=strict, PrivateTmp=true).
97|PAN CLEF benchmark evaluation runner (MRR, nDCG@10, Recall@10).
98|Automated log rotation, WAL checkpointing, and clean teardown.
99|Zero regression against PAN benchmark baseline; automated service recovery under simulated crash; 0 memory leaks under 100 concurrent scans.
100|4. Operational Invariants & Definition of Done
101|Zero Persistent Storage Invariant: At no point in the lifecycle of any scan may retrieved third-party HTML, PDF, or full-text content be written to persistent disk storage. All scraping, alignment, and scoring must occur strictly in RAM buffers and be purged on completion.
102|Deterministic Offset Guarantee: Character offsets reported in the final attribution report must map back exactly to the original uploaded document coordinates, irrespective of formatting conversions.
103|Strict Search Quota Budgets: Every document has an enforced hard ceiling on external search queries (default: 25 queries per 1,000 words). If the budget is exhausted, the search engine halts gracefully and reports partial coverage rather than blowing past cost limits.
104|Revision Delta Invariant: When a submission provides a parent_scan_id or matches an existing revision tree, unchanged chunks with identical cryptographic content hashes must reuse existing alignment results with zero redundant SerpAPI calls.
105|Length-Invariant Accuracy Guarantee: System performance must exhibit zero degradation across the entire 50 to 5,000 word spectrum, maintaining Recall >= 85% and Precision >= 90% in all length tiers through adaptive routing, dense micro-shingles for short text, and distributed spatial probing for long text.
