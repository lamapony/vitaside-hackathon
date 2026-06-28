# Health Patterns MCP — Roadmap

**Last updated:** 2026-06-27 · **MVP tag:** `mvp-1.0` · **Tests:** `python3 test_mvp.py` green

---

## Status summary

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0 — Omi foundation | ✅ Complete | MCP, signals, scoped paths |
| Phase 1 — Apple Health + merge | ✅ Complete | XML, demo fallback, Omi↔Apple by date |
| Phase 1.5 — Hackathon depth | ✅ Complete | Sidecar, what-if, HTML reports, UI, Azure stub, clinical tools |
| Phase 2 — Intelligence polish | 🟡 Mostly done | See remaining items below |
| Phase 3 — Clinical output | 🟡 Partial | HTML ✅, PDF ❌, charts basic |
| Phase 4 — Automation | ⚪ Not started | Scheduled import, export detection |

---

## Phase 0 — Omi foundation ✅
- [x] MCP server on FastMCP
- [x] Omi `.md` parsing (frontmatter + body)
- [x] Signals: sleep, stress, mood_low, mood_good, symptom, food, headache, …
- [x] Date co-occurrence + lag correlations
- [x] `generate_doctor_report`
- [x] Scoped path safety + sidecar manifest enforcement

## Phase 1 — Apple Health ✅
- [x] `load_apple_health_data` — export.xml or demo
- [x] `analyze_apple_patterns` — HR, HRV, sleep, steps, SpO2 trends
- [x] `combine_omi_and_apple` — merge by date (sleep/stress alignment)
- [x] Doctor report includes Apple analysis
- [x] Large export iterparse (>50 MB)
- [x] README + mcporter tests

## Phase 1.5 — Hackathon depth (shipped beyond original roadmap) ✅
- [x] Sidecar protocol: manifest, TTL, scopes, audit log, issue/revoke scripts
- [x] `simulate_whatif` with confidence + disclaimer
- [x] Quality gates: citations, confidence, disclaimer on all tool outputs
- [x] HTML patient timeline + doctor view (`report_html.py`, `report_doctor.py`)
- [x] Local dashboard UI (`ui/` + `api_server.py` + `./serve-ui.sh`)
- [x] Smart analytics: personal baselines, weekday effects, attention-now
- [x] Condition packs (migraine, bipolar), journals, headache insights
- [x] Clinical summary, visit questions, N-of-1 compare, FHIR bundle export
- [x] Azure hybrid contract (stub mode — no credentials required for demo)
- [x] Skin photo ABCDE **observations only** (no risk score, no diagnostic flags)
- [x] Privacy: vault resolves via `OMI_VAULT_PATH` → `~/Documents/Obsidian Vault` → demo (no hardcoded user paths)

## Phase 2 — Intelligence layer (remaining)
- [x] Enhanced Omi parsing (context words, speaker separation, quality scoring, time-of-day)
- [x] Lag correlations with p-values / lift / citations
- [x] Personal baseline bands + weekly summary + period compare
- [x] Local cite-grounded narrative (`narrative_engine.py`)
- [ ] Regime / change-point detection (`detect_regime_shifts` — planned in DEPTH-SPRINT S3)
- [ ] FDR (q_value) on all correlation outputs in UI cards
- [ ] Bootstrap confidence intervals on top correlation lift

## Phase 3 — Clinical output (remaining)
- [x] HTML reports for visits (patient + doctor)
- [x] Obsidian export + visit bundle (`export_visit_bundle`, `export-for-doctor.sh`)
- [x] Anonymization mode
- [ ] PDF export (print CSS or weasyprint)
- [ ] Rich inline charts (sleep / HRV / steps) beyond current timeline bars

## Phase 4 — Automation (not started)
- [ ] Scheduled Apple Health import
- [ ] New export.xml detection
- [ ] Baseline vs current comparison alerts

---

## Apple Health export

iPhone: Settings → Privacy → Health → Export All Health Data.

Large exports (100+ MB) use iterparse; full SAX streaming for multi-GB files is a future improvement.

## Verify

```bash
./setup.sh
python3 test_mvp.py          # ~56 checks + API contract
./run-demo-full.sh --hardening
./serve-ui.sh                # dashboard at :5173
```

See also: `../../plan/DEPTH-ROADMAP.md` for post-MVP human milestones (real vault, doctor feedback).
