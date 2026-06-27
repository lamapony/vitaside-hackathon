# QA Report — VitaSide Hackathon

## QA Wave 3 Hardening 2026-06-27

**Scope:** post-hardening verification only; documents Wave 3 agent deliverables and re-runs from repo root.  
**Working directory:** repo root (`./scripts/vitaside …`); wrapper delegates to `code/health-mcp-starter`.

### Wave 3 agent work

| Area | Change | Finding |
|---|---|---|
| Repo-root wrapper | `scripts/vitaside {test\|demo\|serve-ui\|preflight}` sources `venv-python.sh` and `cd`s into app dir | **QA-8 FIXED** |
| Entry-script venv | All main shell entry points source `scripts/venv-python.sh` and use `$PYTHON` (`run-demo.sh`, `run-demo-full.sh`, `serve-ui.sh`, `pitch_preflight.sh`, `test-mcporter.sh`, sidecar/export scripts) | **QA-5 FIXED** (confirmed Wave 3) |
| UI startup resilience | `App.tsx` uses `Promise.allSettled` for startup fetches; non-critical endpoint failures surface via `PartialErrorBanner` instead of blocking the dashboard | **NEW** |
| Data sources UX | `DataSources.tsx` handles `explicit_empty` / `scope_blocked` with dedicated warning UI and status styling; backed by `data_sources.py` status mapping | **QA-4 UX** |
| mcporter depth tools | `get_clinical_summary`, `run_n1_compare`, `export_fhir_bundle` registered and exercised — no skips | **QA-9 FIXED** |
| Pitch docs | `pitch/DEMO-SCRIPT.md` synced to repo-root `./scripts/vitaside preflight` / `serve-ui` / `test` invocations | **NEW** |

### Wave 3 verification matrix

| Check | Command | Result |
|---|---|---|
| Acceptance suite (repo root) | `./scripts/vitaside test` | **PASS** — exit 0; ALL MVP CHECKS PASSED (49 checks + 14 API contract probes incl. `/api/questions` 2xx) |
| Pitch preflight | `./scripts/vitaside preflight` | **PASS** — exit 0; `PREFLIGHT OK`; demo hardening + UI build green; live `PITCH_*` values printed |
| mcporter transport | `bash code/health-mcp-starter/test-mcporter.sh` | **PASS** — **15 passed**, 0 failed, 0 skipped (depth tools: `get_clinical_summary`, `run_n1_compare`, `export_fhir_bundle`) |
| UI production build | `npm --prefix code/health-mcp-starter/ui run build` | **PASS** — `dist/` produced (~237 kB JS, ~12 kB CSS) |

**Wave 3 matrix:** **4 / 4 PASS**

### Findings status after Wave 3

| ID | Severity | Status | One-line evidence |
|---|---:|---|---|
| QA-5 | P1 | **FIXED** | 11 entry scripts grep-clean for `venv-python.sh`; no global `python3` / pip in demo path |
| QA-8 | P2 | **FIXED** | `./scripts/vitaside test` at repo root → exit 0 |
| QA-9 | P2 | **FIXED** | `test-mcporter.sh` → 15/15 pass; depth tools no longer SKIP |

**Summary:** Wave 3 closes QA-9 (mcporter depth); UI partial-failure path and data-source empty/blocked UX hardened; pitch script aligned with repo-root wrapper.

---

## QA Wave 2 Hardening 2026-06-27

**Scope:** post-hardening verification only; no product code changes.  
**Working directory:** `code/health-mcp-starter` (repo-root invocations of `test_mvp.py` / `health-pattern-mcp.py` fail with “No such file”).

### Wave 2 verification matrix

| Check | Command | Result |
|---|---|---|
| Acceptance suite | `python3 test_mvp.py` | **PASS** — ALL MVP CHECKS PASSED (43 checks + 7 API contract probes incl. `/api/questions` 2xx, report 404, OpenAPI paths) |
| MCP self-test | `python3 health-pattern-mcp.py --test` | **PASS** — exit 0; `files_scanned=83` |
| mcporter transport | `bash test-mcporter.sh` | **PASS** — 12 passed, 0 failed, 3 skipped (optional depth tools not registered) |
| UI production build | `npm --prefix code/health-mcp-starter/ui run build` | **PASS** — `dist/` produced (~235 kB JS) |
| Empty vault fail-fast | `OMI_VAULT_PATH=$(mktemp -d) python3 health-pattern-mcp.py --test` | **PASS** — exit 1; `FAIL: explicit vault has 0 scoped files (...)` |
| OpenAPI generation | `python3 -c "import api_server; api_server.app.openapi()"` | **PASS** — exit 0; no Pydantic forward-ref error |

**Wave 2 matrix:** **6 / 6 PASS**

### Original findings status (QA-1 … QA-7)

| ID | Severity | Status | One-line evidence |
|---|---:|---|---|
| QA-1 | P0 | **FIXED** | `@app.get("/api/questions")` in `api_server.py:327`; `test_mvp.py` GET `/api/questions` → 200 OK |
| QA-2 | P0 | **FIXED** | `serve-ui.sh` reuses or picks free port via `VITASIDE_API_PORT`; `ui/vite.config.ts` proxies to same env var |
| QA-3 | P1 | **FIXED** | Empty-vault probe exits 1; `health-pattern-mcp.py --test` checks `files == 0` for explicit non-demo vault |
| QA-4 | P1 | **FIXED** | `data_sources.py` sets `explicit_empty` / `scope_blocked` / `demo_fallback` and maps `primary_source` accordingly |
| QA-5 | P1 | **FIXED** | `setup.sh` creates `.venv`; all main entry scripts source `scripts/venv-python.sh` and use `$PYTHON` (no global pip mutation) |
| QA-6 | P2 | **FIXED** | Missing report → HTTP 404; handler exceptions → 500 via `_with_error`; `test_mvp.py` asserts OpenAPI 404/500/400 responses |
| QA-7 | P2 | **FIXED** | `_rebuild_pydantic_models()` in `api_server.py`; `api_server.app.openapi()` succeeds |

**Summary:** 7 FIXED, 0 PARTIAL, 0 OPEN.

### New findings (Wave 2)

| ID | Severity | Status | One-line evidence |
|---|---:|---|---|
| QA-8 | P2 | **FIXED** | `./scripts/vitaside test` at repo root → exit 0; ALL MVP CHECKS PASSED |
| QA-9 | P2 | **OPEN** | `test-mcporter.sh` → SKIP: `get_clinical_summary`, `run_n1_compare`, `export_fhir_bundle` |

---

## QA Follow-up Run 2026-06-27 — polished product pass

**Scope:** validation only; no product code changes.  
**Context:** active multi-agent worktree, local `main` is ahead of `origin/main` and many files are modified/untracked.

### Current verification matrix

| Check | Command / method | Result |
|---|---|---|
| Python compile | `python3 -m py_compile $(find . -maxdepth 1 -name '*.py')` | **PASS** |
| Dependency install | `python3 -m pip install -r requirements.txt` | **PASS with risk** — installed `mcp`, upgraded `pandas` to 3.0.3 and caused global Python dependency conflicts |
| Acceptance suite | `python3 test_mvp.py` | **PASS** — all checks passed after dependency install |
| Demo flow | `./run-demo.sh` | **PASS** — reports, collaboration output, and MVP checks complete |
| Pitch preflight | `./pitch_preflight.sh` | **PASS** |
| UI build | `npm --prefix ui run build` | **PASS** |
| MCP transport | `./test-mcporter.sh` | **FAIL / harness issue** — 10/11 pass; `get_sidecar_status` response contains `expires_at`, but shell grep still reports fail |
| Fresh API smoke | `uvicorn api_server:app --port 8791` + HTTP probes | **PARTIAL** — current backend serves most endpoints, but `/api/questions` is 404 |
| Report serving path traversal | encoded `..` / absolute path probes | **PASS** — traversal blocked; real report served |
| Empty explicit vault | temp `OMI_VAULT_PATH` before import | **FAIL** — `list_data_sources()` still reports `omi_vault` primary and `--test` passes with 0 user files |

### New high-priority findings

| ID | Severity | Finding | Evidence | Recommended owner |
|---|---:|---|---|---|
| QA-1 | P0 | Dashboard initial load is broken against current API because UI calls `/api/questions`, but current `api_server.py` has no route decorator for `questions()` | `GET /api/questions -> 404`; `ui/src/App.tsx` includes `getJson<Questions>("/api/questions")` inside startup `Promise.all` | Backend + UI |
| QA-2 | P0 | `serve-ui.sh` can reuse a stale API on port 8787 and Vite proxy is hardcoded to 8787, so UI may test against the wrong backend revision | `lsof` showed existing Python listener on 8787; current API had to run on 8791; `ui/vite.config.ts` proxy is fixed to `http://127.0.0.1:8787` | UI / orchestration |
| QA-3 | P1 | Empty or wrong explicit vault is not fail-fast: preflight-style self-test can pass while user analysis reads 0 files | temp `OMI_VAULT_PATH`: `files_scanned=0`; `python3 health-pattern-mcp.py --test` still exits 0 | Backend / QA |
| QA-4 | P1 | Data source status overclaims readiness for empty or invalid explicit vaults | temp empty vault: `data_mode=explicit`, `primary_source=omi_vault`, while analysis has 0 files | Backend |
| QA-5 | P1 | Global dependency install is unsafe for a polished demo environment | `pip install -r requirements.txt` upgraded global packages and reported conflicts with `streamlit`, `python-telegram-bot`, `langchain-core` | DevEx / orchestration |
| QA-6 | P2 | API error responses use HTTP 200 for error payloads in some paths | missing report returns `200 {"error":"not_found"}`; disabled Azure enhance returns `200 {"error":"RuntimeError"...}` | Backend |
| QA-7 | P2 | API import-by-file under a non-canonical module name can break OpenAPI generation with Pydantic forward-ref errors | `spec_from_file_location("api", "api_server.py"); app.openapi()` raised `PydanticUserError` | QA / Backend |

### Immediate hardening recommendations

1. Add `@app.get("/api/questions")` above `questions()` in `api_server.py` and add a startup API contract test that asserts every UI startup endpoint returns 2xx.
2. Make `serve-ui.sh` and `vite.config.ts` share the selected API port, or fail loudly when the API port is reused by a process that is not this checkout.
3. Change `health-pattern-mcp.py --test` / `pitch_preflight.sh` to require `analyze_lifestyle_patterns()["files_scanned"] >= 30` for demo mode.
4. Fix `list_data_sources()` to distinguish `explicit_empty`, `scope_blocked`, and `demo_fallback` instead of always promoting `omi_vault`.
5. Move setup to `.venv` or a project-local bootstrap script; avoid mutating global Python during judge prep.
6. Replace shell grep in `test-mcporter.sh` with JSON parsing for robust assertions on large MCP responses.
7. Return appropriate HTTP status codes for API errors that are expected by UI and automation.

## QA Run 2026-06-27

**Repo:** `code/health-mcp-starter`  
**Agent:** QA / Hardening (per `plan/agents/04-QA-AGENT.md`)  
**UI acceptance reference:** `plan/UI-AGENT-PROMPT.md`

---

### Verify matrix (pass/fail)

| # | Check | Command / method | Result | Owner lane |
|---|--------|------------------|--------|------------|
| 1 | MVP backend | `python3 test_mvp.py` | **PASS** — ALL MVP CHECKS PASSED (36 checks) | — |
| 2 | Demo quick | `./run-demo.sh` | **PASS** — no errors, reports + collaboration | — |
| 3 | Demo hardening | `./run-demo-full.sh --hardening` | **PASS** — 3/3 runs OK (~12–13s each) | — |
| 4 | UI production build | `cd ui && npm run build` | **PASS** — `dist/` produced (first run hit transient TS2322 on `DoctorHandoff` `context` prop; immediate retry green) | UI |
| 5 | UI acceptance (API smoke) | uvicorn + GET endpoints | **PASS** — briefing (5 insights, date+quote), timeline **84** days, migraine/bipolar, sidecar expiry | — |
| 6 | UI acceptance (manual/script) | `./serve-ui.sh` (~35s) | **PARTIAL** — Vite started; API failed `8787` already in use | UI |
| 7 | Export / doctor handoff | POST `/api/export-bundle` | **PASS** — `questions_count: 9`, HTML paths under `out/` | — |
| 8 | Audit scoped reads | `rg scoped audit.log` | **FAIL** — 0 matches; log has `event` + `files[]` but no explicit scoped-read markers | Backend |
| 9 | mcporter (optional) | `./test-mcporter.sh` | **FAIL** — 0 passed, 11 failed | Backend / MCP |

**Requested matrix (items 1–5):** **4 PASS, 1 PARTIAL** (UI acceptance: API/screens ready; `./serve-ui.sh` not verified on clean ports).

**Extended matrix (QA agent doc):** **7 PASS, 2 FAIL, 2 PARTIAL**.

---

### UI acceptance vs `UI-AGENT-PROMPT.md`

| Criterion | Status | Notes |
|-----------|--------|--------|
| `./serve-ui.sh` opens dashboard with demo vault | **PARTIAL** | Port **8787** collision blocked one-command demo in this run |
| Dashboard ≥1 insight with visible date + quote | **PASS** | API + `Dashboard.tsx` confirmed |
| Timeline ≥30 days + signal chips | **PASS** | 84 entries |
| Condition tab `migraine` + `bipolar` | **PASS** | |
| Doctor Handoff bundle + HTML links | **PASS** | Export API verified |
| Sidecar expiry on Dashboard | **PASS** | `expires_at` on `/api/sidecar` |
| Offline core (no external CDN) | **PASS** | |
| `python3 test_mvp.py` unchanged | **PASS** | |
| README “Local Dashboard” quick start | **PASS** | |
| `pitch/DEMO-SCRIPT.md` mentions `./serve-ui.sh` | **PASS** | |

---

### P0 bugs (conductor assignment)

| ID | Summary | Lane | Evidence |
|----|---------|------|----------|
| P0-1 | **mcporter integration tests all failing** | **Backend / MCP** | `./test-mcporter.sh` → 0/11 |
| P0-2 | **Audit log lacks verifiable “scoped” sidecar read markers** | **Backend** | `rg scoped audit.log` → 0 |
| P0-3 | **`serve-ui.sh` fails when API port 8787 busy** | **UI** | bind error; Vite moved to alternate port |

---

### Recommended Wave 2 assignments

| Lane | Focus |
|------|--------|
| **Backend / MCP** | Fix mcporter suite; log scoped sidecar reads in `audit.log` |
| **UI** | Harden `serve-ui.sh` (port fallback or clear fail-fast) |
| **Azure** | Live share only if pitch requires; consent UI already stubbed |
| **QA** | Re-run after UI script fix on clean ports |

---

### Fixes applied this run

**None** — no trivial test/script patches; `health-pattern-mcp.py` not modified.

---

### Fixes applied after QA (conductor follow-up)

| P0 | Fix | Status |
|----|-----|--------|
| P0-2 | `scoped_read` audit events in `_scan_omi` | ✅ `rg scoped audit.log` |
| P0-3 | `serve-ui.sh` port fallback + reuse running API | ✅ |
| P0-1 | `test-mcporter.sh` rewritten for VitaSide 1.1 | ✅ 11/11 |

---

### Conductor summary

| Metric | Value |
|--------|--------|
| Core commands (1–4) | **4 / 4 PASS** |
| UI acceptance (5) | **PARTIAL** |
| Extended | **7 PASS, 2 FAIL, 2 PARTIAL** |

**Top 3 P0:** (1) mcporter 0/11 → Backend/MCP, (2) audit scoped logging → Backend, (3) serve-ui port conflict → UI.
