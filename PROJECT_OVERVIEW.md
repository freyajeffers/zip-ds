1|High-Level Project Overview
2|Zero-Ingestion Architecture   Privacy-Preserving   On-Demand Retrieval
3|1. Executive Summary & Mission
4|The Zero-Ingestion Plagiarism Detection Service (ZIP-DS) is an enterprise-grade academic and editorial integrity platform designed to eliminate the operational, legal, and infrastructure costs of mass data ingestion. Traditional plagiarism engines require continuously scraping petabytes of web pages and permanently storing millions of student submissions. ZIP-DS rearchitects the detection paradigm by treating public web search engines, open academic knowledge graphs, and privacy-preserving mathematical sketches as on-demand discovery layers.
5|By combining intrinsic stylometric anomaly detection (spotting within-document stylistic shifts without external corpora) with query-chunk provenance modeling (formulating high-specificity quoted shingles and POS-filtered search queries), ZIP-DS retrieves candidate sources ephemerally, performs character-level alignment in memory, and purges source documents immediately upon completion.
6|2. Core Architectural Philosophy
7|Zero Persistent Source Ingestion: External web pages and academic papers are fetched ephemerally into RAM for sequence and embedding alignment and purged immediately. No third-party copyright liabilities or storage bloat.
8|Offline-First & Local Sovereignty: Intrinsic stylometry, local fingerprinting (Winnowing), and dense semantic embeddings execute entirely on local hardware (CPU via ONNX Runtime and FastEmbed) with zero third-party telemetry.
9|Strict Search Budgeting: Multi-stage triage ensures commercial search APIs are queried only when intrinsic analysis or initial verbatim shingles justify an external search, bounding cost to cents per submission.
10|Privacy by Design (FERPA & GDPR Compliant): Submissions are never permanently indexed or shared across institutions in cleartext. Cross-institutional collusion checking is performed strictly via one-way Locality-Sensitive Hashes (MinHash sketches) and cryptographic Bloom filters.
11|Incremental Delta Processing & Multi-Draft Optimization: Cryptographic chunk hashing (BLAKE3) prevents redundant compute and API costs across document revisions (Draft 1 to Draft N), eliminating self-plagiarism false positives while enabling sub-second re-scans.
12|Length-Invariant Processing Framework (50 to 5,000 Words): Adaptive routing handles short (50–300 words), standard (301–1,500 words), and long (1,501–5,000 words) texts, preventing small-sample statistical failure on short submissions and spatial blind spots on long documents.
13|3. End-to-End System Topology
14|The system is organized into a modular, decoupled pipeline structured across six distinct execution layers:
15|Layer
16|Subsystem
17|Primary Responsibility
18|Execution Mode

20|Layer 1
21|Document Ingestion & Sanitization
22|Extract clean text from PDF, DOCX, and TXT; strip boilerplates, structural templates, and reference bibliographies; apply BLAKE3 differential hashing for multi-draft delta tracking.
23|Local Worker (Synchronous)
24|Layer 2
25|Intrinsic Stylometry Engine
26|Compute lexical density, Yule's K, function word distributions, author baseline tracking across revisions, and CUSUM change-point detection across sliding windows with length-adaptive routing.
27|Local Worker (CPU multi-core)
28|Layer 3
29|Query Formulation & Search Dispatcher
30|Decompose suspicious chunks into quoted 8-word shingles and POS-filtered boolean tuples with distributed spatial probing; dispatch against SerpAPI (Google Search & Google Scholar) and academic APIs.
31|Async HTTP I/O (Rate-limited)
32|Layer 4
33|Ephemeral Retrieval & Snippet Triage
34|Evaluate snippet Jaccard scores; fetch HTML/PDF of top candidates into RAM; extract clean text via Trafilatura.
35|Ephemeral RAM Worker
36|Layer 5
37|Dual-Tier Alignment Engine
38|Tier 1: Winnowing & Smith-Waterman for exact matches. Tier 2: Bi-encoder cosine similarity & cross-encoder verification.
39|ONNX Runtime CPU / Local
40|Layer 6
41|Scoring, Reporting & Attribution
42|Aggregate similarity percentages, map character offset spans, and generate interactive, source-grounded audit reports.
43|FastAPI / JSON / HTML
44|4. Technology Stack & Key Dependencies
45|Runtime & Process Model: Python 3.11+, systemd user services, asyncio for non-blocking I/O.
46|Storage & Caching: Embedded SQLite with Write-Ahead Logging (WAL mode), memory-mapped I/O (256 MB), and strict transaction semantics.
47|Parsing & Extraction: trafilatura for web article extraction, pdfplumber for academic PDFs, python-docx for submissions.
48|Intrinsic & Stylometric NLP: NLTK / spaCy (POS tagging, tokenization), SciPy / NumPy (CUSUM, Yule's K calculation).
49|Semantic Embeddings & Inference: ONNX Runtime on CPU, BAAI/bge-small-en-v1.5 for bi-encoder sentence embeddings, quantized cross-encoders for re-ranking.
50|External APIs: SerpAPI (unified gateway for Google Search and Google Scholar), OpenAlex REST API, Semantic Scholar API, Crossref API.
51|5. Security & Isolation Architecture
52|Filesystem Isolation: Absolute path canonicalization and symlink verification on all upload inputs to eliminate path traversal vulnerabilities.
53|Service Sandboxing: Systemd execution profiling with ProtectSystem=strict, ProtectHome=read-only, PrivateTmp=true, and NoNewPrivileges=true.
54|Memory & Resource Limits: Memory mapping caps, per-request execution timeouts (30s SLA), and bounded query heuristics to prevent denial-of-service via malformed documents.
