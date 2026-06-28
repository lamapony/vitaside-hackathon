# Product Sprints — Gap Closure Log

## Sprint P1 — Real Data Loop ✅
- [x] Explicit `OMI_VAULT_PATH` never silently falls back to demo
- [x] Multi-path Omi scan (Conversations, Daily Notes, Journal, `VITASIDE_OMI_PATHS`)
- [x] Large Apple Health iterparse (>50MB)
- [x] Obsidian export (`format=obsidian`)

## Sprint P2 — Doctor Handoff ✅
- [x] `generate_visit_questions` tool
- [x] `export-for-doctor.sh` / `export_visit_bundle`
- [x] Anonymization flag on reports
- [x] Print-ready doctor CSS

## Sprint P3 — Sidecar Ecosystem ✅
- [x] `sidecars/registry.yaml`
- [x] `list-sidecars.sh`
- [x] `revoke-sidecar.sh` + `revoked_at` in manifest

## Sprint P4 — Analytics Depth ✅
- [x] p-values on correlations (exploratory)
- [x] `weekly_summary_report`
- [x] `compare_periods`

## Sprint P5 — Audit hardening ✅ (2026-06-27)
- [x] Skin ABCDE observational-only (no risk score)
- [x] Privacy-first vault path resolution
- [x] requirements.txt complete (pillow, python-multipart)
- [x] Skin API Form() + size limit + graceful errors
- [x] Plan docs synced to code reality

## Next (P6)
- [ ] PDF export
- [ ] Hermes live `needs_context` flow
- [ ] Sidecar registry → auto MCP config writer
