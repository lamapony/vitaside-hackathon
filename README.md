# VitaSide Hackathon Project

**VitaSide** — The Sidecar Protocol for Agentic Personal Health Intelligence

## Quick Start (judges / demo)

```bash
cd code/health-mcp-starter
pip install -r requirements.txt
chmod +x run-demo.sh
./run-demo.sh
```

This runs: self-test → pattern analysis → **what-if simulation** on 90-day demo data.

### MCP server (Hermes / Cursor)

```bash
export OMI_VAULT_PATH="/path/to/your/obsidian/vault"   # or leave default + demo fallback
python3 health-pattern-mcp.py
```

### Tools available

| Tool | Purpose |
|---|---|
| `analyze_lifestyle_patterns` | Omi + Apple patterns, lags, anomalies |
| `simulate_whatif` | Project changes from historical good/bad sleep periods |
| `generate_doctor_report` | Markdown / JSON / HTML export |
| `find_correlation` | Pairwise lag correlation |
| `list_data_sources` | Vault status |

## Plans

- **Rocket plan (active):** `plan/ROCKET-PLAN.md`
- Spec: `docs/SPEC.md`
- Pitch: `VitaSide-Hackathon-Pitch.md`
- Demo script: `pitch/DEMO-SCRIPT.md`

## Status (Sprint 0–4)

- [x] Git repo + requirements + `simulate_whatif`
- [x] Demo data generator + `run-demo.sh`
- [x] Quality gates: confidence + citations + disclaimer on insights
- [x] HTML timeline report (`generate_doctor_report(format="html")`)
- [x] Sidecar protocol: manifest loader, scope check, TTL, audit.log
- [x] `issue-sidecar.sh sleep-stress-sidecar`
- [ ] Collaboration demo script (Sprint 5)
- [ ] Demo hardening 3× (Sprint 6)

## Data note

Real Omi vault is used when `OMI_VAULT_PATH` has parseable conversation notes.
If empty, the server auto-falls back to bundled demo data for a reliable live demo.

**Disclaimer:** Personal lifestyle patterns only — not a medical diagnosis.
