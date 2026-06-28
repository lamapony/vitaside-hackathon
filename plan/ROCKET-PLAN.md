# VitaSide — Rocket Plan (Gap-Driven Execution)

> **Status (2026-06-27): ALL CORE SPRINTS COMPLETE.** This doc is the original 48h hackathon plan, updated to reflect what shipped. Use [`plan/README.md`](README.md) for current backlog.

**North Star demo (achieved):**
`issue → load → ask → analyze (с цитатами) → what-if → beautiful HTML timeline → export → audit`

**Positioning (unchanged):** personal pattern intelligence for self-awareness and doctor visit prep. No diagnosis claims. No risk scores. Disclaimer everywhere.

---

## Code reality (updated 2026-06-27)

| Компонент | Было в плане | Сейчас |
|---|---|---|
| Omi parser (контекст, спикеры, quality) | ✅ работает | ✅ + citations, multi-path scan |
| Apple Health XML | ⚠️ базовый | ✅ merge by date, iterparse large exports |
| Temporal correlations + lift | ✅ | ✅ + p-values, q_value (partial), citations |
| Anomalies / baseline | ⚠️ примитив | ✅ personal baselines in smart_analytics |
| HTML report | ❌ заглушка | ✅ `report_html.py` timeline |
| `simulate_whatif` | ❌ нет | ✅ shipped |
| Sidecar manifest + loader | ❌ нет | ✅ `sidecar_protocol.py` |
| `issue-sidecar.sh` | ❌ нет | ✅ + revoke, registry |
| Audit log | ❌ нет | ✅ `audit.log` (gitignored) |
| Collaboration demo | ❌ нет | ✅ `collaboration_demo.py`, `collaborative_insight` |
| Quality gates | ⚠️ частично | ✅ `_with_gates` on all tools |
| git | ❌ нет | ✅ repo initialized |
| **Bonus (post-plan)** | — | UI dashboard, clinical summary, N-of-1, FHIR, Azure stub, skin ABCDE (observational) |

---

## Sprint status

### Sprint 0 — Foundation ✅
- [x] git + `.gitignore`, `requirements.txt`, README quick-start
- [x] Smoke-test: `python health-pattern-mcp.py --test` green

### Sprint 1 — `simulate_whatif` ✅
- [x] MCP tool with projected_outcomes, confidence, disclaimer

### Sprint 2 — Quality Gates + цитаты ✅
- [x] Excerpts with dates, confidence on insights, global disclaimer

### Sprint 3 — Beautiful HTML Timeline ✅
- [x] `generate_doctor_report(format="html")` → real timeline, not JSON dump

### Sprint 4 — Protocol + Issuance + Audit ✅
- [x] manifest.yaml, scope enforcement, issue-sidecar, audit.log, TTL

### Sprint 5 — Collaboration Demo ✅
- [x] Main + sidecar combined insight; real Omi↔Apple merge

### Sprint 6 — Demo Hardening & Pitch ✅
- [x] `run-demo.sh`, `run-demo-full.sh --hardening`, `pitch/DEMO-SCRIPT.md`

---

## Post-rocket shipped (not in original scope)

These were built during Depth Sprint / UI waves — **do not re-plan as "missing":**

- Local dashboard UI (`ui/`, `api_server.py`, `./serve-ui.sh`)
- Smart analytics layer (`smart_analytics.py`, attention-now, weekday effects)
- Data sources catalog + analysis mechanics docs in MCP tools
- Clinical summary, visit questions, N-of-1 compare, FHIR bundle
- Condition packs, multi-journal, headache insights
- Azure hybrid contract (stub — live needs credentials)
- Skin photo ABCDE observations (rewritten 2026-06-27: **no risk_score, no diagnostic flags**)
- Audit hardening: privacy-first vault resolution, pillow in requirements, API Form() upload fix

---

## Honest remaining (stretch → backlog)

| Item | Priority | Notes |
|------|----------|-------|
| PDF export | P2 | Print CSS or weasyprint |
| Azure live | P2 | Contract ready; stub demos fine for judges |
| Hermes live delegation | P3 | Script simulation works for demo |
| Regime detection + FDR in UI | P3 | DEPTH-SPRINT S3 |
| Real vault + Apple export | P1 human | See DEPTH-ROADMAP D1 |
| E2E skin upload tests | P2 | Consent + invalid image cases |

---

## What we correctly did NOT do

- No ML diagnosis or risk scores (skin tool was corrected to observational-only)
- No deep anomaly ML
- No new data sources beyond Omi + Apple + manual logs
- No medical device claims

---

**Historical note:** Sections below preserved the original gap-driven sprint text. Refer to sprint status above for truth.

<details>
<summary>Original sprint details (archived)</summary>

### Sprint 0 — Foundation (30–45 мин)
- [x] `git init`, `.gitignore`, first commit
- [x] `requirements.txt` + README
- [x] Smoke-test green

### Sprint 1 — `simulate_whatif` (3–4 ч)
- [x] Tool + historical period comparison + confidence

### Sprint 2 — Quality Gates (2 ч)
- [x] Citations, confidence, disclaimer on every insight

### Sprint 3 — HTML Timeline (3 ч)
- [x] Timeline bars, patterns, what-if block

### Sprint 4 — Protocol (2–3 ч)
- [x] Manifest, issuance, audit, TTL

### Sprint 5 — Collaboration (1.5–2 ч)
- [x] Combined insight script + Omi↔Apple merge

### Sprint 6 — Hardening (2–3 ч)
- [x] One-command demo, pitch script, 3× dry-run path

</details>
