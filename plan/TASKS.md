# VitaSide Hackathon Tasks

**Synced:** 2026-06-27 · **Verify:** `./scripts/vitaside test` or `python3 code/health-mcp-starter/test_mvp.py`

Use /plan style: small tasks, one at a time. Items marked ✅ are done in code; ⚪ are honest remaining work.

---

## Phase 1: Spec ✅
- [x] Create `docs/SPEC.md`
- [x] Define HealthPatternSkill workflow

## Phase 2: Plan ✅
- [x] Rocket plan: `plan/ROCKET-PLAN.md`
- [x] Detailed plan: `plan/DETAILED-IMPLEMENTATION-PLAN.md`
- [x] Status dashboard: `plan/README.md`

---

## Build Tasks (Core)

| # | Task | Status |
|---|------|--------|
| 1 | Sidecar manifest loader + scope enforcement | ✅ |
| 2 | Omi parser: timestamps, context words, speakers, quality, time-of-day | ✅ |
| 3 | Apple Health XML (sleep, HR, activity, SpO2, large export iterparse) | ✅ |
| 4 | Temporal correlations (lags), baseline, scipy/pandas stats | ✅ |
| 5 | `simulate_whatif` tool | ✅ |
| 6 | HTML timeline reports + citations | ✅ |
| 7 | Audit logging for data access | ✅ |
| 8 | `issue-sidecar.sh` + revoke + registry | ✅ |
| 9 | Collaboration demo (main + sidecar) | ✅ |
| 10 | Quality gates: confidence, sources, disclaimer | ✅ |
| 11 | Demo data generator + `run-demo.sh` / `run-demo-full.sh` | ✅ |
| 12 | Local dashboard UI + `api_server.py` | ✅ |
| 13 | Smart analytics (baselines, weekday, attention) | ✅ |
| 14 | Clinical summary + N-of-1 + FHIR export | ✅ |
| 15 | Azure hybrid contract (stub) | ✅ stub |
| 16 | Skin ABCDE observations (no risk score) | ✅ hardened 2026-06-27 |
| 17 | Privacy: no hardcoded vault paths; pillow in requirements | ✅ hardened 2026-06-27 |

---

## Test Tasks

| # | Task | Status |
|---|------|--------|
| 11 | Acceptance suite `test_mvp.py` (~56 checks + API contract) | ✅ |
| 12 | mcporter integration `test-mcporter.sh` (15 tools) | ✅ |
| 13 | End-to-end demo `run-demo-full.sh --hardening` | ✅ |
| 14 | Scoped access / no data leaks (sidecar_protocol) | ✅ partial — revoke/expire edge cases |
| 15 | Unit tests for isolated parser functions | ⚪ only via integration tests today |
| 16 | E2E skin upload (consent, bad image, size limit) | ⚪ API manually verified, not in test_mvp |

---

## Review & Polish

| # | Task | Status |
|---|------|--------|
| 15 | Code cleanup, docs | 🟡 plans synced 2026-06-27 |
| 16 | Performance (<30s analysis on demo vault) | ✅ demo vault passes |
| 17 | Simplify outputs for judges | ✅ |
| 18 | Visual assets for pitch | ✅ `docs/index.html`, `pitch/` |

---

## Ship ✅

| # | Task | Status |
|---|------|--------|
| 19 | One-command runner | ✅ `./scripts/vitaside demo` |
| 20 | Pitch script | ✅ `pitch/DEMO-SCRIPT.md` |
| 21 | Demo dry-run 3× | ✅ `--hardening` |

---

## Next (post-hackathon backlog)

1. Real `OMI_VAULT_PATH` + Apple Health export (human setup — DEPTH-ROADMAP D1)
2. PDF export for doctor bundle
3. Azure live (credentials)
4. Hermes live delegation
5. `regime_detection.py` + FDR in UI (DEPTH-SPRINT S3 remainder)
6. E2E skin tests in `test_mvp.py`

**Rule:** Do not reopen completed build tasks unless regressing. Extend tests for new backlog items only.
