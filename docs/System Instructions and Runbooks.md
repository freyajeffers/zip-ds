# System Instructions & Operational Runbooks

------------------------------------------------------------------------

Operational Runbooks   Deployment Guide   Diagnostic Procedures

## 1. Host & Workstation Prerequisites

------------------------------------------------------------------------

- Operating Platform: Linux workstation or server running a modern
  distribution (Debian 12, Ubuntu 22.04 LTS, or Fedora).
- Language Runtime: Python 3.11 or newer with standard development
  tooling (virtual environments, pip).
- Underlying Database: SQLite 3.38+ with Write-Ahead Logging and FTS5
  enabled.
- Compute Hardware: 4 or more physical CPU cores for quantized ONNX
  Runtime embedding inference; minimum 4GB RAM.

## 2. Environment Setup & Configuration

------------------------------------------------------------------------

### 2.1 Virtual Environment Initialization

Initialize a dedicated virtual environment and install project
dependencies:

python3 -m venv .venv\
source .venv/bin/activate\
pip install --upgrade pip\
pip install -r requirements.txt\
pip install google-search-results\

### 2.2 Local Neural Model Synchronization

Download the quantized sentence transformer weights for local offline
inference without external telemetry:

python3 -m zip_ds.scripts.fetch_models --model BAAI/bge-small-en-v1.5\

### 2.3 Service Configuration Parameters

Configure operational settings in the local configuration file
(restricted to permissions 0600):

- SEARCH_API_PROVIDER: Target search service (Bing, Brave, or Google
  Custom Search).
- SERPAPI_API_KEY: Primary authentication key for SerpAPI search engine
  access (defaults configured for google and google_scholar engines).
- OPENALEX_CONTACT_EMAIL: Email identifier for academic polite pool rate
  limits.
- CACHE_DATABASE_PATH: Local filesystem path for the SQLite WAL query
  cache.
- MAX_QUERIES_PER_DOCUMENT: Hard limit on external search calls
  (recommended: 20 per 1,000 words).
- SNIPPET_SIMILARITY_THRESHOLD: Minimum Jaccard score to fetch full text
  (default: 0.20).

## 3. Linux Daemon Supervison & Sandboxing

------------------------------------------------------------------------

The service is designed to run as an isolated background daemon using
systemd user supervision with strict process boundaries.

### 3.1 Service Unit Properties

- Process Restart: Configured with Restart=on-failure and a 5-second
  restart backoff.
- Filesystem Sandboxing: Uses ProtectSystem=strict and
  ProtectHome=read-only, permitting read-write access only to designated
  application state directories.
- Privilege Demotion: Uses NoNewPrivileges=true and an empty capability
  bounding set.
- Private Namespaces: Uses PrivateTmp=true to isolate scratch memory and
  temporary pipes.

### 3.2 Service Management Commands

loginctl enable-linger \$USER\
systemctl --user daemon-reload\
systemctl --user enable --now zip-ds.service\
systemctl --user status zip-ds.service\
journalctl --user -u zip-ds.service -f\

## 4. Operational Verification Runbooks

------------------------------------------------------------------------

### 4.1 Automated Test Execution

pytest tests/unit -v --cov=zip_ds\
pytest tests/integration -v\

### 4.2 Manual Test Scan Execution

python3 -m zip_ds.cli scan test_document.pdf --output report.html\

## 5. Diagnostic & Troubleshooting Matrix

------------------------------------------------------------------------

Observed Issue

Probable Root Cause

Corrective Action

 

Search API HTTP 429 Status

Query burst rate exceeded, or SerpAPI monthly account search credits and
quota exhausted.

Verify SerpAPI dashboard credit usage and quota limits; confirm token
bucket rate limiter settings and ensure secondary provider fallback is
active.

Analysis Latency Exceeds 30s

External web scrapers hanging on slow or protected target sites.

Verify scraper timeout is capped at 3.0 seconds; ensure snippet
pre-filter threshold prunes low-match URLs.

SQLite Concurrency Lock Errors

Missing WAL mode or transaction spanning slow network I/O.

Confirm PRAGMA journal_mode=WAL; verify busy timeout is 5000ms; keep
write transactions strictly local.

CPU Thread Contention

ONNX Runtime inter-op thread pool over-subscribing logical cores.

Pin intra-op threads to physical core count and restrict inter-op
threads to 1.
