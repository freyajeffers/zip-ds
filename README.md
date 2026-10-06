1|Zero-Ingestion Plagiarism Detection Service (ZIP-DS)
2|Open Source Platform   Zero Data Crawl   Local & Private
3|1. Overview
4|The Zero-Ingestion Plagiarism Detection Service (ZIP-DS) is an academic integrity and content attribution system designed from first principles to eliminate the massive storage, maintenance, and legal overhead of crawling and permanently ingesting web corpora.
5|Rather than competing with commercial search engines to index the open web, ZIP-DS pairs intrinsic stylometric anomaly detection (identifying stylistic shifts inside a single document) with query-chunk provenance modeling (formulating high-precision search queries for public search engines and academic graphs). External candidates are fetched ephemerally into memory, aligned with dual-tier lexical and semantic models, and discarded without persistent storage.
6|2. Core Feature Highlights
7|Zero Persistent Storage of Source Corpora: Never store or index third-party text or student submissions. Completely compliant with GDPR "right to be forgotten" and student copyright regulations.
8|Intrinsic Stylometric Triage: Scans sliding windows for vocabulary shifts, Yule's K anomalies, and function-word divergence using CUSUM change-point detection.
9|Budgeted Meta-Search Engine: Synthesizes quoted 8-word shingles and POS-filtered boolean tuples; interfaces with SerpAPI (driving Google Search and Google Scholar) as the primary search retrieval provider, alongside Bing, Brave, and OpenAlex.
10|Dual-Tier Alignment: Combines Winnowing local fingerprinting and Smith-Waterman local alignment for exact text with quantized ONNX Runtime bi-encoders for paraphrased passages.
11|Interactive Attribution Reports: Produces self-contained HTML reports with exact character offsets, color-coded highlights, and direct source links.
12|Hardened Linux Daemon: Fully managed via systemd user services with strict sandboxing and user lingering.
13|Iterative Revision & Multi-Draft Optimization: Uses differential cryptographic chunk hashing (BLAKE3) to detect exact unchanged text between Draft N and Draft N+1, reusing cached alignment results to deliver sub-2s incremental re-scans with up to 90% reduction in SerpAPI query consumption, while actively suppressing false-positive self-plagiarism flags.
14|Length-Invariant Accuracy (50 to 5,000 Words): Eliminates accuracy degradation across all submission sizes—using dense micro-shingles and collocation suppression for short texts (50-300 words) and distributed spatial probe guarantees with sub-linear query budgeting for long papers (up to 5,000 words).
15|3. System Architecture & Pipeline Flow
16|[User Document: PDF / DOCX / TXT]
│
▼
19|[Layer 1: Sanitization & Reference Stripping]
│
▼
22|[Layer 2: Intrinsic Stylometric Triage (CUSUM / Yule's K)]
│ (Identifies High-Risk Anomalous Segments)
▼
25|[Layer 3: Query Formulation (Quoted Shingles & POS Tuples)]
│ (Dispatches to SerpAPI [Google Search/Scholar], Web & OpenAlex APIs)
▼
28|[Layer 4: Ephemeral In-Memory Scraping & Trafilatura Filtering]
│
▼
31|[Layer 5: Dual-Tier Alignment (Winnowing + FastEmbed/ONNX)]
│ (Calculates Exact Character Offsets & Purges RAM)
▼
34|[Layer 6: Deduplicated Scoring & HTML Attribution Report]
35|
36|4. Quickstart
37|# 1. Clone repository and install dependencies
38|git clone https://github.com/organization/zip-ds.git
39|cd zip-ds
40|python3 -m venv .venv && source .venv/bin/activate
41|pip install -r requirements.txt
42|
43|# 2. Download quantized local embedding model
44|python3 -m zip_ds.scripts.fetch_models --model BAAI/bge-small-en-v1.5
45|
46|# 3. Run a scan via command-line interface
47|python3 -m zip_ds.cli scan sample_essay.pdf --output report.html
48|
49|5. Documentation Suite Navigation
50|This project is fully specified across dedicated Google Drive documents in the project workspace:
51|High-Level Project Overview: Executive architecture, layer topology, technology inventory, and threat models.
52|Master Phased Implementation Plan: Five-phase roadmap, cross-phase dependencies, milestones, and definition of done.
53|Phase-by-Phase Technical Specifications: Granular data contracts, component responsibilities, algorithms, and acceptance gates for Phases 1 through 5.
54|AGENTS.md: Operational invariants, coding agent constraints, TDD protocols, and performance SLAs.
55|System Instructions & Runbooks: Prerequisites, systemd daemon installation, sandboxing configs, and diagnostic matrix.
