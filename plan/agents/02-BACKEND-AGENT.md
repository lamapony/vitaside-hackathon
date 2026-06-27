# Backend / Intelligence Agent

## Role
Own **analysis meat** — MCP server, smart analytics, data sources. No React.

**Repo:** `code/health-mcp-starter/`  
**Do NOT edit:** `ui/**`

## Already shipped ✅
- `smart_analytics.py` — baselines, weekday, attention
- `data_sources.py` — catalog + pipeline + live status
- `narrative_engine.py` — local cite-grounded prose
- MCP: `smart_analysis`, `get_local_narrative`, `list_data_sources`, `get_analysis_mechanics`

## Your backlog (pick in order)

### P1 — Apple depth (partial today)
- [ ] SpO2, sleep analysis types in `apple_merge.py`
- [ ] Surface in `merge_with_omi` insights

### P2 — Performance
- [ ] Profile `_scan_omi` + analysis < 30s on demo vault
- [ ] Cache timeseries within single request if needed

### P3 — Tests
- [ ] `test_smart_analytics.py` unit tests
- [ ] `test_data_sources.py` resolution tests

### P4 — Depth sprint S1+S3 ✅
- [x] `clinical_summary.py` + `get_clinical_summary` MCP + `/api/clinical-summary`
- [x] `n1_compare.py` + `run_n1_compare` + `/api/n1-compare`
- [x] `fhir_export.py` + `export_fhir_bundle` + `/api/fhir-preview`
- [x] FDR (`apply_fdr`) on correlation p-values
- [x] Doctor HTML v2 via clinical summary in `report_doctor.py`

### P5 — Hermes prep
- [ ] Export `mcp-config.example.json` with all new tools listed
- [ ] `needs_context` response shape in `collaborative_insight` (stub)

## Verify
```bash
cd code/health-mcp-starter
python3 test_mvp.py
python3 -c "import importlib.util; ..."
```

## Report to conductor
- Files changed
- New MCP tools (if any)
- API additions for UI agent
