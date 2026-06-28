# Visit packet slice (VIT-26)

**Epic:** VIT-23 / VIT-26  
**Branch:** `vitaside/visit-packet-mcp`  
**Closed:** 2026-06-28 (Integration Engineer)

## Scope delivered

- MCP tool `build_visit_packet(formats?, anonymize?, include_whatif?)` in `health-pattern-mcp.py`
- Returns `VisitPacket`-shaped JSON: `visit_date`, `entity_id`, `summary_md`, `questions[]`, `included_patterns[]`, `personal_baselines`, `outputs`, `confidence`, `citations`, `pain_point_citations`, `disclaimer`
- Composes `generate_doctor_report`, `generate_visit_questions`, optional `export_fhir_bundle`
- **VIT-25 wiring:** syncs journal entries → SQLite via `get_personal_baselines_payload`; baselines embedded in packet + vault note
- **Vault output:** `demo-data/vault/03-Visits/Visit-Prep-{date}-GP.md` (manifest scope `read`/`write`)
- **KG:** golden entity `vp-20260628-gp` ↔ [[Visits/Visit-Prep-2026-06-28-GP]] in `KG-ENTITY-REGISTRY.md`
- **PP-01** cited in template (`export_obsidian.PP01_PAIN_POINT_CITATION`)
- Canonical probe `health_check` wraps `get_sidecar_status` + optional `list_data_sources`

## VERIFY

```bash
cd health-mcp-starter
pytest tests/test_visit_packet.py -q   # includes E2E <60s offline
bash test-mcporter.sh                  # build_visit_packet + health_check
python3 test_mvp.py
pytest tests/ -q
```

## References

- [[../../../VitaSide-Research/04-Architecture/mcp-tool-surface.md]] §6
- [[../../../VitaSide-Research/08-Planning/hermes-vitaside-verify-report.md]]