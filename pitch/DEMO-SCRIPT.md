# VitaSide Live Demo Script (Sprint 6 — final flow)

**One command before judges:** `./run-demo-full.sh --hardening`

**Single dry-run:** `./run-demo.sh`

---

## Pre-flight (5 min)

```bash
cd code/health-mcp-starter
pip install -r requirements.txt
./run-demo-full.sh --hardening   # must pass 3/3
open out/vitaside-report-$(date +%Y-%m-%d).html   # bookmark this tab
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
