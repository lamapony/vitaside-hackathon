# Doctor handoff print export (VIT-43)

**Issue:** VIT-43  
**Assignee:** Integration Engineer  
**Depends:** VIT-26 ✅, G1 (VIT-29) ✅

## Scope

Visit markdown from `build_visit_packet` → **print-optimized HTML** with mandatory footer:

- Data scope (manifest `allowed_scopes`)
- Audit summary (local `audit_summary`)
- Disclaimer + packet confidence + `entity_id`

PDF: use browser **Print → Save as PDF** on the generated HTML (no extra Python deps in CI).

## Code

| Piece | Path |
|-------|------|
| Renderer | `doctor_handoff_export.py` |
| MCP tool | `export_doctor_handoff_print` in `health-pattern-mcp.py` |
| Tests | `tests/test_doctor_handoff_export.py` |
| Golden markers | `fixtures/doctor_handoff_print_markers.txt` |

## Operator / demo VERIFY

```bash
cd code/health-mcp-starter
export OMI_VAULT_PATH="$(pwd)/demo-data/vault"
export VITASIDE_MANIFEST="$(pwd)/sidecars/sleep-stress-sidecar/manifest.yaml"
pytest tests/test_doctor_handoff_export.py -q
# Optional live:
python3 -c "import importlib.util; ..."  # or mcporter call export_doctor_handoff_print
open out/doctor-handoff-print-$(date +%F).html   # print preview — no PHI in repo
```

## Acceptance

- [x] Demo packet → `out/doctor-handoff-print-*.html`
- [x] Footer contains scope, audit, disclaimer, confidence
- [x] Golden marker fixture passes on demo
- [ ] Manual print preview path in vault (operator, no PHI) — `08-Planning/VIT-43-print-preview.md` when captured

## Links

- Visit template: vault KG visit-prep skill
- UI: `ui/src/pages/DoctorHandoff.tsx` (API `/api/export-bundle` — separate path)