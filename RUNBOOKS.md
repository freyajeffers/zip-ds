1|System Instructions & Operational Runbooks
2|Operational Runbooks   Deployment Guide   Diagnostic Procedures
3|1. Host & Workstation Prerequisites
4|Operating Platform: Linux workstation or server running a modern distribution (Debian 12, Ubuntu 22.04 LTS, or Fedora).
5|Language Runtime: Python 3.11 or newer with standard development tooling (virtual environments, pip).
6|Underlying Database: SQLite 3.38+ with Write-Ahead Logging and FTS5 enabled.
7|Compute Hardware: 4 or more physical CPU cores for quantized ONNX Runtime embedding inference; minimum 4GB RAM.
8|2. Environment Setup & Configuration
9|2.1 Virtual Environment Initialization
10|Initialize a dedicated virtual environment and install project dependencies:
11|python3 -m venv .venv
12|source .venv/bin/activate
13|pip install --upgrade pip
14|pip install -r requirements.txt
15|pip install google-search-results
16|
17|2.2 Local Neural Model Synchronization
18|Download the quantized sentence transformer weights for local offline inference without external telemetry:
19|python3 -m zip_ds.scripts.fetch_models --model BAAI/bge-small-en-v1.5
20|
21|2.3 Service Configuration Parameters
22|Configure operational settings in the local configuration file (restricted to permissions 0600):
23|SEARCH_API_PROVIDER: Target search service (Bing, Brave, or Google Custom Search).
24|SERPAPI_API_KEY: Primary authentication key for SerpAPI search engine access (defaults configured for google and google_scholar engines).
25|OPENALEX_CONTACT_EMAIL: Email identifier for academic polite pool rate limits.
26|CACHE_DATABASE_PATH: Local filesystem path for the SQLite WAL query cache.
27|MAX_QUERIES_PER_DOCUMENT: Hard limit on external search calls (recommended: 20 per 1,000 words).
28|SNIPPET_SIMILARITY_THRESHOLD: Minimum Jaccard score to fetch full text (default: 0.20).
29|3. Linux Daemon Supervison & Sandboxing
30|The service is designed to run as an isolated background daemon using systemd user supervision with strict process boundaries.
31|3.1 Service Unit Properties
32|Process Restart: Configured with Restart=on-failure and a 5-second restart backoff.
33|Filesystem Sandboxing: Uses ProtectSystem=strict and ProtectHome=read-only, permitting read-write access only to designated application state directories.
34|Privilege Demotion: Uses NoNewPrivileges=true and an empty capability bounding set.
35|Private Namespaces: Uses PrivateTmp=true to isolate scratch memory and temporary pipes.
36|3.2 Service Management Commands
37|loginctl enable-linger $USER
38|systemctl --user daemon-reload
39|systemctl --user enable --now zip-ds.service
40|systemctl --user status zip-ds.service
41|journalctl --user -u zip-ds.service -f
42|
43|4. Operational Verification Runbooks
44|4.1 Automated Test Execution
45|pytest tests/unit -v --cov=zip_ds
46|pytest tests/integration -v
47|
48|4.2 Manual Test Scan Execution
49|python3 -m zip_ds.cli scan test_document.pdf --output report.html
50|
51|5. Diagnostic & Troubleshooting Matrix
52|
53|Observed Issue
54|Probable Root Cause
55|Corrective Action

57|Search API HTTP 429 Status
58|Query burst rate exceeded, or SerpAPI monthly account search credits and quota exhausted.
59|Verify SerpAPI dashboard credit usage and quota limits; confirm token bucket rate limiter settings and ensure secondary provider fallback is active.
60|Analysis Latency Exceeds 30s
61|External web scrapers hanging on slow or protected target sites.
62|Verify scraper timeout is capped at 3.0 seconds; ensure snippet pre-filter threshold prunes low-match URLs.
63|SQLite Concurrency Lock Errors
64|Missing WAL mode or transaction spanning slow network I/O.
65|Confirm PRAGMA journal_mode=WAL; verify busy timeout is 5000ms; keep write transactions strictly local.
66|CPU Thread Contention
67|ONNX Runtime inter-op thread pool over-subscribing logical cores.
68|Pin intra-op threads to physical core count and restrict inter-op threads to 1.
