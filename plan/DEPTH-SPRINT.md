# VitaSide — Sprint по углублению (Science + Integration + Clinical Utility)

> **Status (2026-06-27):** S1, S2, S3 **core deliverables shipped**. S4–S6 partial / backlog.  
> **Verify:** `python3 test_mvp.py` · **Backlog:** `plan/README.md`

| Sprint | Goal | Status |
|--------|------|--------|
| S1 Clinical Summary | 3-min doctor handoff | ✅ `clinical_summary.py`, doctor HTML, UI DoctorHandoff |
| S2 PGHD / FHIR | EHR-ready bundle | ✅ `fhir_export.py` — validator / HAPI test ⚪ |
| S3 N-of-1 & Science | Causal-ish moat | ✅ `n1_compare.py`, p-values — regime detection, FDR in UI ⚪ |
| S4 Integration Hub | Azure + Hermes live | ⚪ stub only |
| S5 UI Depth | OpenDesign polish | ✅ 6 tabs — mobile/a11y audit ⚪ |
| S6 Real data | 60+ day loop | ⚪ human process |

---
> **Цель:** не «чат с LLM про здоровье», а **Personal Health Intelligence Layer** —
> локальная наука на *ваших* данных + понятный handoff в клинику.
>
> **Уже есть (не переписывать):** Omi parser, lag correlations + p-values, personal baselines,
> weekday effects, what-if, condition packs, cite-grounded narrative, sidecar protocol,
> doctor HTML, clinical summary, N-of-1, FHIR export, PGHD context + auto-suggestions,
> OpenDesign UI, Azure contract (stub), skin ABCDE observations (no risk score).

---

## Позиционирование (одной фразой)

**ChatGPT** отвечает из training data. **VitaSide** считает паттерны на вашем vault,
хранит provenance, выдаёт **N-of-1 insights с цитатами** и **сжатый clinical summary**
для врача — без диагноза и без raw stream в EHR.

---

## Тренды 2025–2026 (зачем это системе здравоохранения)

| Тренд | Источник / смысл | Что делает VitaSide |
|-------|------------------|---------------------|
| **PGHD → EHR** | AHRQ Practical Guide, HL7 PGHD IG | FHIR Observation bundle, не сырые транскрипты |
| **SMART on FHIR / API** | 21st Century Cures, vendor surveys | Sidecar = scoped API; export = consented bundle |
| **Clinical fatigue** | npj Digital Medicine 2025 | **Binning**: weekly trends, flags, не каждая заметка |
| **Sociotechnical responsibility** | Кто реагирует на anomaly? | Manifest: TTL, audit, disclaimer, no auto-alert to clinic |
| **N-of-1 / Per-DS** | PMC personalized data science | What-if + personal baselines = proto N-of-1 |
| **Temporal phenotyping** | AMIA/JMIR self-track + EHR | Signal states over time + condition packs |

Ссылки: [AHRQ PGHD Guide](https://digital.ahrq.gov/patient-generated-health-data), [HL7 PGHD IG](https://build.fhir.org/ig/HL7/personal-health-record-format-ig/en/pghd.html), [npj sociotechnical PGHD](https://www.nature.com/articles/s41746-025-01680-5).

---

## Три аудитории — три продукта в одном

```
┌─────────────────────────────────────────────────────────────┐
│  PATIENT          │  DOCTOR              │  SYSTEM (EHR)   │
│  Command center   │  3-min handoff       │  FHIR + APIs    │
│  Next steps       │  Questions + trends  │  PGHD summary   │
│  My context       │  No raw chat logs    │  Audit/provenance│
└─────────────────────────────────────────────────────────────┘
         ▲                    ▲                    ▲
         └────────── Local MCP + scientific core ──┘
              (optional Azure = narrative polish only)
```

---

## Scientific Core — что добавить поверх текущей статистики

### Уровень 1 — уже есть ✅
- Lag correlations + lift + exploratory p-values
- Personal baseline bands (`smart_analytics.py`)
- Weekday / weekend effects
- Historical what-if (`simulate_whatif`)
- Cite-grounded local narrative (`narrative_engine.py`)

### Уровень 2 — Sprint S-Science (2–3 недели)
| Метод | Зачем | Deliverable |
|-------|-------|-------------|
| **N-of-1 period compare** | «A weeks vs B weeks» для интерvention | `run_n1_compare(exposure, outcome, window)` |
| **Granger-lite / precedence** | Cause before effect с lag distribution | Улучшить `find_correlation` + confidence bands |
| **Change-point detection** | «С марта стало хуже» | `detect_regime_shifts(signal, min_days=14)` |
| **Multiple testing control** | Меньше ложных паттернов | Benjamini–Hochberg на top correlations |
| **Effect size + CI** | Для врача: не только p | Bootstrap CI на lift для top-3 |
| **Wearable fusion score** | Omi + Apple same-day | `merge_confidence` в merged insights |

### Уровень 3 — исследование (после 60+ real days)
- Simple **U-CATE-style** counterfactual labels (not full g-computation)
- **Temporal phenotypes**: 3–5 interpretable states (stable / stressed / symptomatic)
- Optional ONNX export of personal baseline model (local inference)

**Правило:** каждый новый метод → MCP tool + UI card + **обязательная цитата/число**, не prose.

---

## Sprint Plan (6 спринтов × ~1 неделя)

### Sprint S1 — Clinical Summary Layer (Patient + Doctor)
**Goal:** врач открывает bundle за 3 минуты; пациент видит «so what».

| Task | Owner | Done when |
|------|-------|-----------|
| `clinical_summary.py` — 1-page structure | Backend | Problem list, trends (14/90d), meds from context, top 3 patterns, questions |
| Doctor HTML v2 — summary-first layout | Backend | Above fold: trends + flags, below: citations |
| UI: Weekly recap screen | Frontend | Export + print; link from Command center |
| PDF via print CSS | Backend | `out/vitaside-clinical-summary-*.pdf` |

**Acceptance:** врач без контекста проекта понимает пациента за 3 мин (user test n=1).

---

### Sprint S2 — PGHD / FHIR Export (System)
**Goal:** данные *могут* попасть в EHR, не обязаны.

| Task | Done when |
|------|-----------|
| `fhir_export.py` — Bundle: Patient, Observations (signals), DocumentReference (report) | Valid against PGHD IG patterns |
| Map signals → temporary codes + LOINC where possible (sleep, HR, steps) | Documented mapping table |
| `export_fhir_bundle()` MCP tool + Doctor Handoff button | JSON + optional Azure upload |
| **Binning policy**: weekly aggregates, max 1 excerpt per flag | No raw Omi dump in FHIR |

**Acceptance:** импорт Bundle в HAPI FHIR test server или validator green.

---

### Sprint S3 — N-of-1 & Regime Tools (Science moat)
**Goal:** отличие от LLM — *ваша* causal-ish история.

| Task | Done when |
|------|-----------|
| `n1_compare.py` — exposure weeks vs control weeks | Tool + UI in Smart tab |
| `regime_detection.py` — change points on signal frequency | Flag on Dashboard |
| FDR on correlation list | `analyze_lifestyle_patterns` returns `q_value` |
| Bootstrap CI on top correlation lift | Shown in insight cards |

**Acceptance:** demo vault shows regime shift + N-of-1 card with CI; `test_mvp.py` extended.

---

### Sprint S4 — Integration Hub (Azure + Agents + Sidecars)
**Goal:** hybrid без потери local-first.

| Task | Done when |
|------|-----------|
| Azure agent: live `enhance_insight` + share URL | Contract v1.0 fulfilled |
| `collaborative_insight` live in Hermes | Calendar + sidecar demo |
| Condition sidecar + Azure sidecar composable manifests | Registry documents combos |
| Audit export for compliance story | `export_audit_summary()` |

**Acceptance:** toggle local-only vs hybrid in demo script; audit shows cloud calls.

---

### Sprint S5 — UI Depth (OpenDesign track)
**Goal:** не оболочка — рабочий инструмент.

| Screen | Priority | Must show |
|--------|----------|-----------|
| Timeline v2 | P0 | Heatmap/calendar, dark tokens, drill to citation |
| My context v2 | P0 | Suggestion review split-view |
| Smart v2 | P1 | Baselines, regimes, N-of-1 results |
| Condition v2 | P1 | Pack metrics + doctor focus + link to visit |
| Weekly recap | P1 | New OpenDesign screen |

**Acceptance:** gap-audit vs API — every MCP tool has UI surface.

---

### Sprint S6 — Validation & Evidence (Trust)
**Goal:** доказать пользу, не accuracy диагноза.

| Task | Done when |
|------|-----------|
| `docs/EVIDENCE-MODEL.md` — what we claim / don't claim | Signed off |
| 1 real user (you) — 30 days journal + retrospective | ≥3 insights acted on |
| 1 clinician feedback session on doctor HTML | Notes in `docs/clinician-feedback.md` |
| Comparison doc: VitaSide vs generic LLM on same question | Citations win table |

---

## Integration Architecture (target)

```
Sources                    Core                         Outputs
─────────                  ────                         ───────
Omi vault ──┐
            ├──► Parser ──► Scientific layer ──► Patient UI (Command center)
Apple export ┘              │                    Doctor bundle (HTML/PDF)
                            ├── Condition packs ─► FHIR PGHD bundle
User context ───────────────┤                    Obsidian / visit prep
Sidecar manifest ───────────┘                    Audit log
                                                      │
Optional Azure ◄── consent + minimized JSON only ◄────┘
```

---

## Anti-patterns (не делаем)

- ❌ Diagnosis / risk scores / «AI doctor»
- ❌ Sending full Omi transcripts to cloud by default
- ❌ Real-time alerts to hospital without explicit RPM contract
- ❌ Population norms as primary reference (always personal baseline first)
- ❌ LLM narrative without evidence_map / citations

---

## Metrics (как понять что «реально удобно»)

| Metric | Patient | Doctor | System |
|--------|---------|--------|--------|
| Time to weekly action | <5 min in UI | — | — |
| Visit prep completeness | Profile readiness ≥80% | — | — |
| Handoff time | — | <3 min to grasp case | — |
| FHIR validity | — | — | Bundle validates |
| Insight action rate | ≥2 acted insights / month | — | — |
| vs LLM | 100% top insights have date+quote | — | — |

---

## Recommended execution order

```
Week 1: S1 Clinical Summary  (doctor value immediately)
Week 2: S3 N-of-1 + regimes  (science moat)
Week 3: S2 FHIR export       (system story)
Week 4: S5 Timeline + Context UI (OpenDesign)
Week 5: S4 Azure live        (parallel agent)
Week 6: S6 Validation        (evidence)
```

---

## Next action (pick one to start coding)

1. **S1** — `clinical_summary.py` + doctor HTML v2
2. **S3** — `n1_compare.py` + FDR on correlations
3. **S2** — `fhir_export.py` minimal Bundle

Say which sprint to execute first — or run S1+S3 in parallel (backend / Azure agent).
