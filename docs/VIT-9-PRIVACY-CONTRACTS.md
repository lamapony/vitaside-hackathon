# VIT-9: Privacy contracts research — complete

**Issue:** VIT-9 · **Status:** Delivered in vault `06-Privacy-Contracts/`

## Deliverables

| Path | Content |
|------|---------|
| `vault/06-Privacy-Contracts/_index.md` | Index + contract stack |
| `vault/06-Privacy-Contracts/VIT-9-best-practices.md` | GDPR/HIPAA/PGHD patterns + anti-patterns |
| `vault/06-Privacy-Contracts/azure-minimal-exposure-matrix.md` | Azure OpenAI, Functions/Blob, Search, FHIR controls |
| `vault/06-Privacy-Contracts/templates/*` | Manifest, user consent, outbound JSON policy, issuer attestation |

## Relationship to code (already shipped)

- Enforcement: `azure_contract.py` (`AZURE_SERVICES`, `validate_outbound`)
- Examples: `schemas/azure-payload-*.example.json`
- Architecture survey: `docs/MCP-SIDECAR-TECHNICAL-SURVEY.md` §4
- Service map: `docs/VIT-4-AZURE-HEALTH-EVALUATION.md`

## Verify

```bash
cd code/health-mcp-starter
export VITASIDE_MANIFEST=sidecars/azure-hybrid-sidecar/manifest.yaml
python3 test_mvp.py
python3 -c "from azure_contract import contract_info; from sidecar_protocol import load_manifest; print(contract_info(load_manifest('sidecars/azure-hybrid-sidecar/manifest.yaml'))['strict_controls_note'])"
```

No live Azure credentials required for this issue.