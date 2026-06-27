# VitaSide Live Demo Script (Sprint 6 — final flow)

**One command before judges:** `./run-demo-full.sh --hardening`

**Single dry-run (polished narrative):** `./run-demo.sh`

Shows **actionable briefing** — dated citations, not generic LLM advice.

**Dashboard demo (second screen):** `./scripts/vitaside serve-ui` from repo root (or `./serve-ui.sh` in `code/health-mcp-starter`) — Command center shows **sidecar expiry**; **Data sources** tab lists Omi/Apple scopes; **Doctor handoff** tab exports visit bundle + questions.

---

## The "why not ChatGPT?" line (memorize — verify with `./scripts/vitaside preflight`)

> "ChatGPT can tell you pain affects mood. VitaSide shows that **on March 31** you wrote *«Грустно и тяжело, день прошёл уныло»* and your **own 83 days** of notes show pain→low mood with **~2× lift** — with an audit log of every file read. That's not a chatbot guess."

**What-if line:** sleep stabilization → mood_low **−62%** (confidence **0.95** — from your good vs poor sleep nights).

**Collaboration line:** 4 poor-sleep nights near travel + stress near deadlines — Hermes calendar + sidecar patterns combined.

Run `./scripts/vitaside preflight` before stage — prints live `PITCH_*` values if demo data shifts.

---

## Pre-flight (5 min)

From repo root: `./scripts/vitaside preflight` (acceptance via `./scripts/vitaside test`). Or:

```bash
cd code/health-mcp-starter
pip install -r requirements.txt
./pitch_preflight.sh              # 5 min — must say PREFLIGHT OK
./run-demo-full.sh --hardening   # must pass 3/3
open out/vitaside-report-$(date +%Y-%m-%d).html   # bookmark this tab
open out/vitaside-doctor-$(date +%Y-%m-%d).html
```

Backup: screenshot `out/` + terminal output. Pre-record `./run-demo-full.sh` once.

---

## Live flow (6–7 min)

### 1. Hook (30s)
> "Doctors see 15-minute snapshots. You live 24/7 with Omi voice notes and Apple Health. VitaSide lets a doctor issue a **temporary AI sidecar** inside your personal agent — local, audited, expiring."

### 2. Issue sidecar (45s)
```bash
./issue-sidecar.sh sleep-stress-sidecar
```
Show `manifest.yaml`: scopes, TTL, issuer.  
> "Patient adds one MCP block. No new app. No cloud."

### 3. Pattern analysis (90s)
```bash
python3 run_demo_check.py analyze
```
Point at **citations** on top correlation.  
> "Not hallucinated — every pattern cites your actual note."

### 4. What-if wow (90s)
```bash
python3 run_demo_check.py whatif
```
> "What if I fixed sleep to 7.5h for two weeks? Sidecar projects from *your* history — confidence 0.95."

### 5. HTML report (60s)
```bash
python3 run_demo_check.py html && open out/vitaside-report-*.html
```
Scroll timeline + pattern cards + audit footer.

### 6. Collaboration (60s)
```bash
python3 collaboration_demo.py
```
> "Hermes knows your flights and deadlines. Sidecar knows sleep and stress lags. **Together** they explain *why* those weeks felt worse."

### 7. Close (30s)
```bash
wc -l audit.log && python3 run_demo_check.py sidecar
```
> "Local. Temporary. Audited. Protocol extensible — any specialist can issue a sidecar. Patterns for awareness, not diagnosis."

---

## Judge Q&A cheatsheet

| Question | Answer |
|---|---|
| Medical device? | No — personal pattern intelligence for self-awareness and visit prep. Disclaimer on every output. |
| Privacy? | Scoped paths, audit.log, TTL expiry, no network. |
| Real data? | Demo vault with planted correlations; swap `OMI_VAULT_PATH` for real Omi vault. |
| vs generic AI coach? | Multi-agent + MCP sidecar protocol + citations + what-if from *your* history. |

---

## If live fails

1. Open pre-generated HTML in `out/`
2. Show `collaboration_demo.py` output screenshot
3. Walk through `docs/SPEC.md` manifest example
