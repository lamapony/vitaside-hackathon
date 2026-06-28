# VIT-3: Technical Methods Survey for MCP Health Sidecar (Local-First + Azure Hybrid)

**Issue:** VIT-3  
**Agent:** Systems Architect (ee8872ad-b2f9-4f81-bad6-a4e3bb7d4369)  
**Date:** 2026-06-28  
**Status:** Survey complete — architecture decisions documented and trade-offs analyzed.  

**Goal:** Compare options for MCP protocol, local data stores, pattern detection methods, privacy contracts, and Azure hybrid options. Produce architecture docs and trade-off analysis suitable for the vault (Obsidian/Aviato structure). This informs future depth sprints and production hardening.

All decisions prioritize:
- Local-first execution (no raw data leaves device by default)
- Privacy by design (data minimization, explicit consent, auditability, TTL scopes)
- Interpretability (user and doctor must understand *why* an insight appeared)
- Hackathon / real-use practicality (simple to run, no heavy infra)
- Optional Azure "boost" only for higher-value scenarios

## 1. MCP / Sidecar Protocol Choice

### Current Implementation
- **Protocol:** Model Context Protocol (MCP) via `mcp.server.fastmcp.FastMCP`
- **Transport:** stdio (standard input/output) — perfect for local agent embedding
- **Integration:** Added to Hermes via `mcp_servers` config (see `mcp-config.example.json`)
- **Manifest:** YAML-driven sidecar issuance (`sidecar_protocol.py`): name, version, issuer, ttl, allowed_scopes (paths + read perms), tools list, quality_gates
- **Tools exposed:** 30+ (analyze_*, simulate_whatif, generate_*, azure_*, skin_*, etc.)
- **Collaboration:** `collaborative_insight` + host context passing; sidecar can signal needs_context
- **Audit:** Local append-only `audit.log` (JSON lines) + manifest TTL enforcement + revoke

### Alternatives Considered
| Option | Description | Pros | Cons | Fit for Local-First Health |
|--------|-------------|------|------|----------------------------|
| **MCP (chosen)** | Stdio tool server with tool discovery, typed params, agent-native | Native to Hermes/agent ecosystems; easy multi-agent delegation; no ports; discoverable tools; lightweight | Dependency on MCP SDK; still maturing standard (2026) | Excellent — zero network, scoped, auditable |
| Custom JSON-RPC over stdio | Roll our own request/response over pipes | Full control; no external dep | Reinvent wheel; less discoverable for agents | Good but higher maintenance |
| Local HTTP (FastAPI + uvicorn) | REST/JSON over localhost:port | Easy to test/curl; familiar; OpenAPI | Requires port management, firewall awareness, more attack surface | Acceptable but violates "no outbound by default" spirit |
| Plugin / entrypoint system (e.g. Python pkg_resources) | Dynamic load as Python module | Zero serialization | Tight coupling; harder to sandbox/expire; security risk for sidecars | Poor for temporary/doctor-issued sidecars |
| gRPC / protobuf | High-perf binary RPC | Efficient for large data | Heavy deps; not agent-native | Overkill for personal use |
| Subprocess + CLI flags/JSON | Shell out and parse stdout | Simple, no libs | Brittle parsing; no structured tools | Used in early prototypes; scaled poorly |

**Trade-off Analysis & Decision:**
- MCP wins for **agent integration** (core use case: "lives as MCP sidecar inside Hermes").
- Stdio eliminates network entirely (local-only default).
- Manifest + scopes provide the "contract" layer missing from raw functions.
- **Risk mitigated:** If MCP changes, we can fallback to custom JSON-RPC (the server already abstracts tools).
- **Evidence:** Works today with `python3 health-pattern-mcp.py`, `mcporter`, `./test_mvp.py`, and UI api_server.py wrapper.

**Recommendation:** Stay with MCP. Extend manifest for more advanced contracts (e.g. `data_minimization_level`).

## 2. Local Data Stores & Persistence

### Current Implementation
- **Primary:** Human-readable files
  - Obsidian Markdown (Omi voice notes + journals) — parsed with regex + speaker/time heuristics
  - Apple Health export.xml (large, streaming iterparse)
- **In-memory / working:** Python dicts + pandas DataFrames (parsed daily entries with signals)
- **Config / state:** YAML/JSON manifests, sidecar YAMLs, demo-data/ seeds
- **Output:** out/*.json, *.html, *.md (Obsidian export), audit.log (append-only)
- **No DB server:** Pure file + process memory. Vault path via `OMI_VAULT_PATH` env (never hardcoded in source after hardening)

### Alternatives Considered
| Store | Description | Pros | Cons | Local-First Score |
|-------|-------------|------|------|-------------------|
| **Files (Markdown + XML) + pandas (chosen)** | Direct parse of user's existing exports | Zero setup; human readable/editable; matches user's current workflow (Obsidian + Apple) | Parsing fragile for noisy Omi; full re-parse each time | Highest — respects existing user data |
| SQLite (local file DB) | Structured relational | Fast queries, indexes, ACID; easy joins on dates | Adds schema migration burden; less "human" | High for analytics layer |
| DuckDB / Parquet | Analytical columnar | Excellent for time-series aggregates, fast on laptop | New file format; users won't edit | Very high for pattern detection |
| JSONL + polars | Lightweight | Fast, no deps beyond polars | Still requires parsing layer | Good |
| Chroma / LanceDB (local vector) | Embeddings for semantic search on notes | Great for "find similar past days" | Vector index overhead; privacy of embeddings | Medium — only if opt-in RAG |
| Full local LLM context window | Load everything into prompt | Simplest "AI does it" | Context limits, cost, privacy (even local) | Poor for 90+ days history |

**Trade-off Analysis & Decision:**
- **Files first** because the value prop is "use the data you already collect" (Omi + Apple + notes). Adding a DB would require import step — friction.
- Pandas chosen for quick stats (correlations, baselines) — familiar, sufficient for N-of-1 personal data (small datasets, 90-180 days).
- **Future hybrid store:** Keep files as source of truth; add optional DuckDB cache for repeated queries (see DEPTH-ROADMAP S3+).
- **Privacy win:** No central store; user can delete files or change path at any time. Sidecar never writes back to vault unless explicit export.

**Current code proof:** `apple_merge.py` (iterparse >50MB), `journal_insights.py`, `data_sources.py`, `gen_demo_data.py`.

## 3. Pattern Detection Methods

### Current Implementation
- **Statistical / rule-based core** (`smart_analytics.py`, `analytics_depth.py`, `journal_insights.py`):
  - Personal baselines (rolling 28-day windows, mean/std/p25/p75 per signal)
  - Lag correlations (1-3 days) with lift, p-values (scipy.stats), FDR correction
  - Weekday/weekend effects, recency weighting
  - Anomalies vs *your* history (not population norms)
  - Condition packs (manual + tracked entries)
  - Simple what-if simulation (apply delta to historical series, re-compute metrics)
- **Narrative layer:** `narrative_engine.py` (template + local LLM fallback) + optional Azure OpenAI for richer prose
- **Quality:** Every output has `confidence`, `citations` (excerpts + dates), `disclaimer`
- **Skin:** Pure descriptive ABCDE features (no ML diagnosis)
- **No population models:** Everything N-of-1

### Alternatives Considered
| Method | Description | Pros | Cons | Privacy / Interpretability |
|--------|-------------|------|------|----------------------------|
| **Personal stats + heuristics (chosen)** | Rolling baselines, lag corr, p-values, rules | Fully interpretable; runs instantly locally; cites exact days | Misses subtle non-linear patterns; sensitive to Omi noise | Excellent — user sees the numbers |
| Pure LLM analysis (local Ollama or Azure) | Feed all entries + ask "find patterns" | Handles nuance/language in Omi notes | Hallucinations, no citations by default, compute heavy | Medium — requires heavy gating |
| Traditional ML (sklearn: clustering, isolation forest, Prophet) | Fit per-user models | Better anomaly detection on wearables | Black-box (hard to cite); training overhead on laptop | Low interpretability without SHAP |
| Time-series DL (LSTM / TFT) | Deep forecasting | Strong for what-if | Overkill, data hungry, not local-first friendly | Poor for explainability |
| Expert system / clinical rules | Hard-coded if-then from literature | Reproducible | Brittle, not personalized, maintenance hell | Good but not adaptive |
| Hybrid: stats base + LLM narrative | Current direction | Best of both | Still needs strong citation enforcement | Good |

**Trade-off Analysis & Decision:**
- **Stats core mandatory** for trust and doctor utility ("show me the p=0.03 on day X").
- LLM only for *presentation* (narrative, doctor report polish) — never for primary detection.
- Omi data is noisy/subjective → heavy emphasis on quality scoring in parser + confidence gates.
- **What-if** is deliberately simple (historical replay with perturbation) to remain auditable.
- **Evidence of correctness:** `test_mvp.py` runs ~56 checks including statistical assertions; reports include citations.

**Recommendation:** Keep statistical foundation. Add optional regime detection / bootstrap CI in DEPTH sprints (see plan/DEPTH-SPRINT.md S3). For skin, stay observational only.

## 4. Privacy Contracts & Sidecar Scoping

### Current Implementation
- **Manifest-driven contract** (`sidecar_protocol.py`, `issue-sidecar.sh`):
  - `allowed_scopes`: list of {path, permissions: ["read"]}
  - `ttl`: "30d" or ISO; auto-expire + is_revoked
  - `enable_azure_boost`, `azure.allowed_operations`, `data_policy.max_excerpt_chars`, `anonymize_by_default`
  - `quality_gates`
- **Enforcement:** `check_scope()`, `assert_sidecar_active()`, `is_expired()`
- **Audit:** Every tool call, scope check, azure call logged with ts + fingerprint (no raw data)
- **Data minimization in Azure payloads** (`azure_contract.py`): only aggregates, top 5 insights, trimmed excerpts (140 chars default), anonymized, no vault paths, no full transcripts
- **Consent:** Explicit `user_consent=True` for any outbound; skin photo requires Form() + consent
- **Revoke / list:** `list-sidecars.sh`, `revoke-sidecar.sh`
- **No PII in code:** Hardened (no dev vault paths)

### Alternatives Considered
| Contract Mechanism | Description | Pros | Cons | Fit |
|--------------------|-------------|------|------|-----|
| **YAML Manifest + scope paths + TTL + audit (chosen)** | Declarative, file-based, enforceable in process | Simple for user/doctor to inspect; git-trackable; no central authority | Manual issuance; path-based (OS specific) | Excellent for personal sidecars |
| Capability tokens (Macaroons / Biscuit) | Cryptographic bearer with attenuation | Fine-grained, delegatable, expirable | Complexity for hackathon; key management | Future (post-MVP) |
| OAuth2 / OIDC scopes | Standard auth | Familiar | Requires auth server; overkill for local | Not local-first |
| Full differential privacy (DP libs) | Noise injection at query time | Strong math guarantees | Reduces utility; complex to tune for N=1 | Overkill now |
| Zero-knowledge proofs | Prove patterns without revealing data | Ultimate privacy | Impractical for health signals today | Research only |
| Signed JWT from doctor | Issuer signs manifest | Clear provenance | Still needs verification code | Good complement to current |

**Trade-off Analysis & Decision:**
- Current manifest is the right simplicity level for MVP + real use.
- Path scoping + audit + TTL gives strong practical control without crypto overhead.
- Azure payloads strictly minimized + consented + fingerprinted.
- **Audit is append-only local file** — user owns it, can review/delete.
- **Future:** Add cryptographic signing of manifests for doctor-issued sidecars (see AZURE-CONTRACT).

**Current proof:** `./issue-sidecar.sh`, `revoke-sidecar.sh`, `azure_contract.build_payload()`, tests enforce consent.

## 5. Azure Hybrid Options

### Current Implementation (see also `docs/azure-hybrid-options.md`, `AZURE-CONTRACT.md`)
- **Stub-first:** `VITASIDE_AZURE_MODE=stub` (default) — full functionality without any cloud.
- **Contract:** `azure_contract.py` builds sanitized payloads; `azure_boost.py` dispatches.
- **Operations (opt-in):**
  - `enhance_insight` → Azure OpenAI (rich narrative from local stats)
  - `share_report` → Azure Function + Blob (time-limited doctor link)
  - Planned: embed_search, fhir_export
- **Data flow:** Local compute everything → minimize → consent gate → (optional) HTTPS → Azure → response
- **Privacy controls:** max_excerpt_chars, anonymize_by_default, no raw data, audit every call
- **Live code:** Partial (URL construction + stub fallback); needs credentials + Function impl for full live

### Alternatives Considered
| Azure / Cloud Path | Description | Usefulness | Privacy / Risk | Hackathon Fit |
|--------------------|-------------|------------|----------------|---------------|
| **Azure OpenAI + Functions (chosen for boost)** | Enrich narrative + host shareable report | High — better doctor reports, share link | Medium (minimized data only) | Strong demo value |
| Full local (Ollama / llama.cpp) | No Azure | Highest privacy | Highest | Good fallback, already partial |
| Azure Health Data Services (FHIR) | Interop with EHR | Very high for real doctors | Low if consented bundle only | Post-hackathon |
| Azure ML / AutoML (export ONNX) | Better models, run local | Medium | High if training data sent | Possible but complex |
| Azure Static Web Apps only | Host UI / reports | Polish | Low | Easy |
| Other clouds (AWS Bedrock, GCP) | Similar | Similar | Similar | Not chosen (Azure hackathon friendly) |
| No cloud ever | Pure local | Max privacy | Max | Core must work this way |

**Trade-off Analysis & Decision:**
- **Hybrid only as boost, never required.** Core always works locally.
- Data minimization + consent + short TTL + audit is the contract (see AZURE-CONTRACT.md).
- **Chosen services prioritized:** OpenAI for narrative (biggest UX win), Functions/Blob for share (demo wow).
- **Risks addressed:** Explicit `enable_azure_boost`, preview_payload tool, no PHI in cloud without consent.
- **Cost:** Free tier + hackathon credits assumed.
- **Lock-in mitigation:** Stub always present; document local LLM alternatives.

**Current state:** Stub complete and tested; live path scaffolded. See `azure_share_server.py` for example Function stub.

## Recommended Target Architecture (Post-Survey)

```
User Device (always local core)
├── Vault (Obsidian Omi + Apple export + journals)  [source of truth, user owned]
├── VitaSide MCP Sidecar (FastMCP + sidecar_protocol)
│   ├── Parsers (Omi, Apple, journals)
│   ├── Personal stats engine (baselines, lags, p-values, what-if)
│   ├── Narrative (local templates + optional local LLM)
│   ├── Reports (md/json/html/Obsidian/FHIR)
│   └── Sidecar manifest enforcement + audit.log
├── Optional Azure Boost (opt-in only)
│   ├── Minimized payload (aggregates + trimmed citations)
│   ├── Azure OpenAI (enhance)
│   └── Azure Functions/Blob (share)
└── UI (local Vite dashboard) + api_server.py (FastAPI wrapper)
```

**Cross-cutting:**
- All outputs gated with confidence + citations + disclaimer
- Manifest as the privacy contract
- No raw data in any cloud path
- User can run 100% offline

## Next Steps (from this survey)
- Reference this doc from `plan/README.md` and `docs/index.html`
- Implement live Azure paths in a follow-up agent wave (credentials + Function)
- Add `get_architecture_survey()` tool to MCP for self-description
- Update `SPEC.md` with survey outcomes
- For DEPTH: evaluate DuckDB cache, signed manifests, regime detection

**Verification commands (run after changes):**
```bash
cd code/health-mcp-starter
./scripts/vitaside test
python3 test_mvp.py
```

This survey is now part of the vault for future reference and audits.

---

**Produced for Paperclip issue VIT-3.**  
All raw analysis stayed local. No external services used in this survey step.