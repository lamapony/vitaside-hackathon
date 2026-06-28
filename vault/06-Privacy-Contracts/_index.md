# 06 — Privacy Contracts (VIT-9)

> **Issue:** Research data minimization contracts and Azure hybrid controls; sample templates for sidecar + cloud handoff.
> Links: [[VIT-9-best-practices]] · [[azure-minimal-exposure-matrix]] · `docs/VIT-9-PRIVACY-CONTRACTS.md` · `docs/AZURE-CONTRACT.md`

## What lives here

| Artifact | Purpose |
|----------|---------|
| [[VIT-9-best-practices]] | External norms + comparable product patterns for health/PGHD minimization |
| [[azure-minimal-exposure-matrix]] | Per-Azure-service controls mapped to VitaSide operations |
| `templates/` | Copy-paste contracts (manifest, consent, outbound JSON policy, issuer attestation) |

## VitaSide contract stack (implemented)

1. **Sidecar manifest** — `allowed_scopes`, `ttl`, tool allow-list (`sidecar_protocol.py`)
2. **Azure gate** — `enable_azure_boost`, `azure.allowed_operations`, `data_policy` (`manifest.yaml`)
3. **Outbound payload** — `azure_contract.build_payload()` + `validate_outbound()` (no raw vault, capped excerpts)
4. **Runtime consent** — `user_consent=True` on live Azure MCP tools; audit fingerprint only in `audit.log`

## Templates

- [[templates/sidecar-scope.template]] — YAML sidecar + optional Azure block
- [[templates/azure-user-consent.template]] — Plain-language consent before cloud boost
- [[templates/outbound-data-contract.template]] — Machine-readable policy snippet (aligns with payload v1)
- [[templates/doctor-issuer-attestation.template]] — Issuer checklist for doctor-issued sidecars

## Code cross-refs

- `code/health-mcp-starter/azure_contract.py` — `AZURE_SERVICES`, `OPERATIONS`, validation
- `code/health-mcp-starter/schemas/azure-payload-*.example.json` — worked examples per operation