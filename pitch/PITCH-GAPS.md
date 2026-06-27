# Pitch gaps & mitigations — 2026-06-27

## ✅ Verified green

| Check | Result |
|-------|--------|
| `./run-demo-full.sh --hardening` | 3/3, ~11–14s per run |
| `python3 test_mvp.py` | 36/36 |
| `bash test-mcporter.sh` | 11/11 |
| HTML reports | report ~16KB, doctor ~2.5KB |
| Sidecar TTL | expires ~2026-07-27 |
| API smoke | health, briefing, smart, timeline, sidecar → 200 |

---

## 🔴 Fixed before pitch

| Gap | Risk | Fix |
|-----|------|-----|
| **DEMO-SCRIPT had wrong numbers** (86 days, 2.2×, wrong quote) | Judge catches mismatch | Updated to 84d, 4.7×, actual Mar 31 quote |
| **UI vs terminal different headline** | Confusion switching screens | Briefing now leads with correlation, not attention |

---

## 🟡 Know these (don't get surprised)

| Topic | Reality | What to say |
|-------|---------|-------------|
| **Correlation confidence 0.37** vs **what-if 0.95** | Different metrics — sample size vs sleep contrast | "Pattern confidence from note chains; what-if from 20+ good/poor sleep nights" |
| **Top pattern is pain→mood**, not sleep→stress | Demo data planting | Lean into it — still shows lag + citation moat |
| **Apple Health = demo synthetic** | `apple_health` status `demo_fallback` | "Wearable merge works; demo uses synthetic Apple — real export is one unzip away" |
| **Doctor HTML is compact** | 2.5KB, no timeline viz | Use **patient report** for timeline scroll; doctor view for table summary |
| **UI needs API running** | `./serve-ui.sh` not in steps 3–7 | Pre-open UI tab before pitch OR use `./serve-ui.sh` as step 2b |
| **Azure** | Stub only | "Optional cloud boost tomorrow — today everything is local" |
| **First run ~15s** | Cold analysis | Pre-run `./run-demo.sh` once; keep HTML tab open |

---

## 🟢 Demo flow recommendation (7 min)

1. **Hook** (script §1)
2. `./issue-sidecar.sh` + show manifest scopes
3. `./run-demo.sh` OR `python3 demo_briefing.py` — **point at Mar 31 quote**
4. `python3 run_demo_check.py whatif` — cite **0.95** and **−62%**
5. Open **patient HTML** — scroll timeline
6. `python3 collaboration_demo.py` — travel + deadlines
7. Optional: **UI Smart tab** — personal baselines (second screen)
8. `wc -l audit.log` — scoped reads

---

## If live fails

1. Pre-opened HTML tabs (`out/vitaside-report-*.html`)
2. Screenshot from last `./run-demo.sh`
3. Walk manifest in `sidecars/sleep-stress-sidecar/manifest.yaml`

---

## 5 min before stage

```bash
cd code/health-mcp-starter && ./pitch_preflight.sh
```

Must print **PREFLIGHT OK** and `PITCH_*` lines — read them once aloud.
