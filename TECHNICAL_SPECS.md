1|Phase-by-Phase Detailed Technical Specifications
2|Architecture Specifications   Data Contracts   Verification Gates
3|
4|Phase 1: Ingestion, Sanitization & Intrinsic Stylometry
5|1.1 Scope & Architectural Responsibilities
6|Phase 1 establishes the document normalization pipeline and the intrinsic stylometric triage engine. It consumes raw user-submitted files, canonicalizes filesystem paths, extracts normalized plaintext while preserving character coordinate offsets, detects and isolates bibliographic reference blocks, and performs sliding-window stylometric anomaly detection without any external network access.
7|1.2 Component Responsibilities
8|Document Extractor: Supports PDF (via pdfplumber), DOCX (via python-docx), and plain text. Applies path traversal validation, resolving real paths and enforcing root confinement.
9|Sanitizer & Offset Tracker: Normalizes UTF-8 characters, strips control sequences, and maps every extracted character to its original source coordinate range [start_char, end_char].
10|Bibliography Isolator: Uses regular expressions and layout heuristics to identify section headings such as "References", "Bibliography", or "Works Cited". Extracts reference list entries into a dedicated metadata structure to prevent false-positive matching against cited works.
11|Intrinsic Stylometry Analyzer:
12|Calculates Average Sentence Length (ASL) and Average Word Length (AWL) over a sliding window of 250 words with a 50-word step.
13|Computes Yule's Characteristic K to measure vocabulary richness and token recurrence distributions.
14|Computes Function Word Ratios across 150 closed-class English grammatical markers (prepositions, conjunctions, pronouns).
15|Runs Cumulative Sum (CUSUM) change-point detection across the sliding windows to identify points where the stylistic vector departs by >2.5 standard deviations from the document mean.
16|Length-Aware Ingestion Routing: Defines three operational regimes based on document size: Micro/Short (50–300 words), Standard (301–1,500 words), and Long/Thesis (1,501–5,000 words). For Micro texts (50–300 words), automatically bypasses statistical CUSUM and Yule's K (unstable on small token samples) and marks the entire text as a direct target. For Long texts (1,501–5,000 words), enforces hierarchical paragraph-section chunking with sliding-window stylometry.
17|Differential Chunk Hashing & Document Lineage: Computes BLAKE3/SHA-256 hashes per normalized chunk to detect unchanged versus modified paragraphs across sequential document revisions (Draft N vs. Draft N+1). Establishes an author-level baseline to track stylistic evolution over time.
18|1.3 Data Contracts & Interface Schemas
19|DocumentChunk:
chunk_id: str (UUIDv4)
chunk_hash: str (BLAKE3/SHA-256)
parent_chunk_id: Optional[str]
start_offset: int
end_offset: int
raw_text: str
token_count: int
is_bibliography: bool
stylometric_scores:
asl: float
awl: float
yules_k: float
function_word_entropy: float
anomaly_z_score: float
is_anomalous: bool (True if anomaly_z_score > 2.5)
35|
36|1.4 Acceptance Criteria & Verification Gates
37|Zero path traversal vulnerabilities confirmed via adversarial test suite (e.g., ../../etc/passwd and symlink escapes).
38|Character offset roundtrip accuracy: 100% exact substring match between reported offsets and original raw file text across 50 sample documents.
39|Bibliography isolation recall ≥ 98% on academic test papers.
40|Stylometric sliding-window computation executes under 100ms per 1,000 words on a single CPU core.
41|
42|Phase 2: Query Formulation & Search Dispatcher
43|2.1 Scope & Architectural Responsibilities
44|Phase 2 translates document chunks into a lean, highly discriminative set of search engine queries. It implements Query-Chunk Provenance Modeling, POS-pattern filtering, and query budgeting to discover candidate URLs from commercial search engines (Google, Bing, Brave) and scholarly graphs (OpenAlex, Semantic Scholar) without exceeding API rate limits or cost ceilings.
45|2.2 Component Responsibilities
46|Query-Chunk Provenance Splitter: Partitions document into semantic chunks (minimum 800 characters, maximum 3,000 characters). Adjacent paragraphs are merged up to the 3,000 character limit, prioritizing sections flagged as stylistically anomalous in Phase 1.
47|Discriminative Query Generator:
48|Verbatim Shingles: Extracts 8–10 consecutive token shingles enclosed in double quotes ("...") targeting unique phrasing.
49|Keyphrase / Boolean Queries: Uses POS tagging to extract noun chunks, proper nouns, and distinctive verb-object pairs. Filters out terms with document frequency in common corpora > 5,000. Formulates 3–5 term boolean queries (e.g., quantum "error mitigation" combinatorial).
50|Query Budget Manager & Adaptive Stopper: Allocates a dynamic budget (default: 15 queries per 1,000 words). If early queries for a chunk yield a verified source with >70% overlap, remaining planned queries for that chunk are canceled.
51|Meta-Search Dispatcher: Asynchronous multi-provider client integrating SerpAPI as the primary unified search gateway alongside direct scholarly API connections:
52|SerpAPI Unified Search Gateway: Dispatches web shingle queries using SerpAPI Google Search (engine='google') for web snippet retrieval, and dispatches academic queries using SerpAPI Google Scholar (engine='google_scholar') for scholarly paper and preprint verification.
53|Scholarly Graph Integration: OpenAlex REST API polite pool and Semantic Scholar Paper API complemented by SerpAPI Google Scholar indexing.
54|SerpAPI Payload Parsing & Response Normalization: Extracts candidate records from organic_results, mapping link to source URL, snippet to text content, and position to candidate rank.
55|SerpAPI Rate-Limiting & Resiliency: Implements token-bucket rate limiting, automatic backoff on HTTP 429 / credit exhaustion signals, and seamless fallback to cached SERP results.
56|SERP Cache Engine: Embedded SQLite cache operating in WAL mode. Keys are SHA-256 hashes of normalized query strings. SERP results are cached with a 7-day TTL to eliminate duplicate billable calls.
57|Delta Querying & Revision Optimization: Evaluates chunk hashes against prior revisions to target query generation exclusively on new or modified content. Bypasses external network calls by reusing cached SERP results and alignment spans for unchanged chunks, reducing API costs and latency by 80–90%. Incorporates self-plagiarism exclusion logic to ignore match hits against prior drafts within the same user session.
58|Length-Proportional Query Formulation & Spatial Coverage: For 50–300 word texts, generates dense overlapping micro-shingles (6–8 tokens, step=2) with idiomatic/common-collocation filtering to prevent false positives. For 1,501–5,000 word texts, enforces a distributed spatial probe guarantee (at least 2 queries per 500 words across the entire document timeline) and a sub-linear dynamic budget ceiling: Budget = clamp(min=3, max=45, ceil(3 + 0.008 * word_count)) to prevent coverage drop-off in later sections.
59|2.3 Data Contracts & Interface Schemas
60|SearchCandidate:
url: str
source_type: Enum[WEB, ACADEMIC_PAPER, REPOSITORY]
title: str
snippet: str
rank_position: int
matched_query: str
originating_chunk_id: str
snippet_jaccard_score: float
69|
70|2.4 Acceptance Criteria & Verification Gates
71|Query budget adherence: strictly ≤ 20 external API queries dispatched per 1,000 words under all test cases.
72|SERP caching verification: 100% cache hit on re-submitting identical query strings within TTL; zero duplicate API requests.
73|Candidate recall ≥ 85% on standard benchmark sets containing known web plagiarism samples.
74|Full token-bucket rate limiter compliance with zero 429 (Too Many Requests) errors under concurrency.
75|
76|Phase 3: Ephemeral Scraping & Dual-Tier Alignment Engine
77|3.1 Scope & Architectural Responsibilities
78|Phase 3 performs ephemeral retrieval and detailed text alignment. It evaluates candidate snippets, fetches raw HTML/PDF of top candidates into in-memory buffers, strips boilerplate, and executes dual-tier alignment (lexical sequence matching and dense embedding semantic comparison). Crucially, all retrieved external texts are discarded from memory immediately after alignment.
79|3.2 Component Responsibilities
80|Snippet Triage Gate: Computes 3-gram Jaccard similarity between search snippet and suspicious chunk. Only candidates with $J(snippet, chunk) \ge 0.20$ are scheduled for network retrieval, discarding 70%+ of irrelevant links before fetching.
81|Ephemeral Scraper: Concurrent asynchronous HTTP client (with browser headers and 5s timeout; adaptive concurrency up to 15 concurrent HTTP requests for long submissions with a strict 2.5s per-domain timeout to keep 5,000-word scans within latency bounds) fetching candidate pages. Uses trafilatura to extract core body text and discard navigation bars, ads, and footers. The raw HTML is never written to disk.
82|Tier 1 Lexical Aligner:
83|Winnowing Fingerprinter: Hashes 5-word shingles across sliding window $w=8$. Compares fingerprint sets to find exact shared subsequences.
84|Smith-Waterman Alignment: Finds local alignment boundaries with match bonus (+2), mismatch penalty (-1), and gap penalty (-1).
85|Tier 2 Semantic Aligner:
86|Splits text into sentences using NLTK/spaCy.
87|Encodes sentences into 384-dimensional dense vectors using local ONNX Runtime CPU inference (BAAI/bge-small-en-v1.5).
88|Computes cosine similarity matrix. Pairs with cosine similarity ≥ 0.82 are flagged as paraphrased plagiarism.
89|Ephemeral Memory Scrubber: Explicitly deletes candidate text buffers and triggers Python garbage collection, guaranteeing no persistent source retention.
90|3.3 Data Contracts & Interface Schemas
91|AlignedMatch:
match_id: str (UUIDv4)
suspicious_chunk_id: str
source_url: str
source_title: str
alignment_type: Enum[VERBATIM, NEAR_VERBATIM, PARAPHRASE]
susp_start_char: int
susp_end_char: int
matched_susp_text: str
matched_source_text: str
confidence_score: float (0.0 - 1.0)
102|
103|3.4 Acceptance Criteria & Verification Gates
104|Verification of Zero Persistent Ingestion: Automated test checks working directory and temporary paths post-execution; zero external source files or cache traces on disk.
105|Tier 1 alignment latency < 50ms per 1,000-word candidate text.
106|Tier 2 semantic alignment detects paraphrased sentences (with synonym substitutions and passive voice reordering) with F1 > 0.88.
107|Robust scraper error handling: graceful degradation on HTTP 403, 404, 500, SSL failures, and timeout with zero unhandled exceptions.
108|
109|Phase 4: Scoring, Report Synthesis & REST API Interfaces
110|4.1 Scope & Architectural Responsibilities
111|Phase 4 unifies the detection pipeline into an production-grade REST service. It computes the deduplicated overall similarity index, synthesizes character-offset attribution maps, generates standalone interactive HTML audit reports with verified source links, and exposes a clean OpenAPI-compliant interface.
112|4.2 Component Responsibilities
113|Score Aggregator & De-duplicator: Merges overlapping match intervals on the suspicious document timeline (using interval trees or interval union algorithms) to prevent duplicate percentage penalties when a single sentence matches multiple online sources.
114|Similarity Index Calculator: $$\text{Similarity Index} = \frac{\sum |Interval_{\text{union}}|}{\text{Total Document Character Count}} \times 100\%$$ Provides granular sub-scores for Verbatim %, Paraphrased %, and Bibliography-excluded matches.
115|Attribution Report Synthesizer: Generates self-contained JSON and HTML inspection reports with color-coded side-by-side highlighting, source cards with clickable URLs, matched snippet previews, and confidence ratings.
116|Revision Evolution Reporting: Tracks similarity score progression across draft iterations (e.g., Draft 1 vs. Draft 2 diffs). Visualizes resolved plagiarism spans alongside newly introduced unoriginal text across revisions.
117|Length-Calibrated Scoring & Collocation Suppression: Requires a minimum contiguous match threshold of 7 tokens or semantic sentence equivalent, preventing short submissions from registering artificially high similarity percentages due to common idiomatic expressions.
118|FastAPI Service Architecture:
119|POST /v1/scans: Accepts file uploads or raw text with optional parent_scan_id; returns job ticket.
120|GET /v1/scans/{scan_id}: Returns status (queued, analyzing, completed, failed) and progress percentage.
121|GET /v1/scans/{scan_id}/report: Returns full JSON / HTML attribution report.
122|4.3 Data Contracts & Interface Schemas
123|PlagiarismReport:
scan_id: str (UUIDv4)
parent_scan_id: Optional[str] (UUIDv4)
document_hash: str (SHA-256)
total_words: int
total_characters: int
overall_similarity_percentage: float
verbatim_percentage: float
paraphrase_percentage: float
revision_delta:
score_change: float
resolved_spans_count: int
new_unoriginal_spans_count: int
sources:

- source_id: int
  url: str
  title: str
  matched_words: int
  coverage_percentage: float
  annotated_spans:
- start: int
  end: int
  source_id: int
  match_type: str
  confidence: float
  148|
  149|4.4 Acceptance Criteria & Verification Gates
  150|Deduplicated interval calculation verified: union of identical overlapping intervals never exceeds 100% or double-counts characters.
  151|End-to-end scan latency < 20 seconds for standard 2,500-word submissions under normal API response times.
  152|Full OpenAPI 3.1 schema compliance with automated contract testing via Schemathesis.
  153|Report HTML self-containment: verified rendering without external CSS/JS CDN dependencies.
  154|
  155|Phase 5: Security Hardening, Systemd Daemonization & PAN Benchmark
  156|5.1 Scope & Architectural Responsibilities
  157|Phase 5 elevates the service to an enterprise-hardened Linux background daemon. It configures systemd sandboxing directives, establishes scheduled database maintenance, pins CPU thread execution pools, and executes a formal evaluation against standardized PAN CLEF plagiarism benchmark datasets.
  158|5.2 Component Responsibilities
  159|Systemd Sandboxing & Service Unit: Standardizes zip-ds.service as a hardened user daemon:
  160|ProtectSystem=strict and ProtectHome=read-only (with read-write access restricted strictly to the SQLite WAL directory and private temp socket).
  161|PrivateTmp=true, NoNewPrivileges=true, ProtectKernelTunables=true.
  162|CapabilityBoundingSet= (empty, dropping all root capabilities).
  163|Self-healing restart policy: Restart=on-failure, RestartSec=5s.
  164|Thread Pinning & Concurrency Hardening:
  165|Locks ONNX Runtime intra-op threads to physical host CPU core counts, setting inter-op threads to 1 to eliminate thread thrashing.
  166|SQLite WAL configured with busy_timeout=5000, mmap_size=268435456 (256MB), and periodic systemd timer for checkpointing (PRAGMA wal_checkpoint(TRUNCATE)).
  167|PAN CLEF Benchmark Suite: Evaluates the system on standard PAN 2014–2026 Source Retrieval and Text Alignment corpora. Measures:
  168|Recall@K and Precision of retrieved candidate documents.
  169|Plagdet Score (harmonic mean of Precision, Recall, and Granularity).
  170|Average Queries & Downloads per document.
  171|5.3 Acceptance Criteria & Verification Gates
  172|Systemd service starts cleanly, survives SIGTERM/SIGKILL with proper resource cleanup, and automatically restarts on unexpected failure.
  173|Service sandboxing passes security audit; unauthorized file write attempts outside the designated state directory trigger immediate permission faults.
  174|Benchmark parity: Plagdet score on PAN test corpus matches or exceeds published baseline literature without persistent corpus indexing.
  175|Memory stability: Zero memory leak detected over 500 continuous scans under load testing.
