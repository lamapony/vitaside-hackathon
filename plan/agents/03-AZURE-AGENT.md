# Azure Hybrid Agent

## Role
Optional cloud layer — **consent-first**, minimized payloads only.

**Own:** `azure_boost.py`, `azure_share_server.py`, `azure_contract.py`, `sidecars/azure-hybrid-sidecar/`

## Current state
- Contract v1.0 + preview payload ✅
- Stub uses `narrative_engine` ✅
- Live hooks exist but need env vars

## Tasks

### P1 — Demo-safe stub polish
- [ ] Ensure `azure_enhance_insight` returns rich local narrative with `evidence_map`
- [ ] Share stub returns realistic TTL preview JSON

### P2 — Live mode (if credentials available)
- [ ] `VITASIDE_AZURE_MODE=live` + Azure OpenAI chat completions
- [ ] Azure Function share URL upload
- [ ] Document env in `docs/AZURE-CONTRACT.md`

### P3 — UI wire (coordinate UI agent)
- [ ] Consent modal contract documented for `POST /api/azure/enhance`

## Never
- Send raw vault paths or full transcripts
- Call network without `user_consent=True`

## Verify
```bash
VITASIDE_MANIFEST=sidecars/azure-hybrid-sidecar/manifest.yaml python3 test_mvp.py
```
