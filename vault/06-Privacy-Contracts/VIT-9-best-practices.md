# VIT-9 — Best practices: health data minimization contracts

**Agent:** Integration Engineer · **Date:** 2026-06-28 · **Scope:** Personal PGHD / N-of-1 sidecars (not full EHR operator).

## 1. Regulatory & framework anchors (what contracts should satisfy)

| Source | Minimization idea | VitaSide mapping |
|--------|-------------------|------------------|
| **GDPR Art. 5(1)(c)** | Adequate, relevant, limited to purpose | Outbound = aggregates + ≤N insights + trimmed citations only |
| **GDPR Art. 25** | Privacy by design/default | Azure off by default; stub mode; preview before send |
| **HIPAA Minimum Necessary** (US, if clinic partner) | Limit PHI disclosed to job | No full transcripts; pseudonymous share links; TTL on blob |
| **FTC Health Breach Notification** | Vendor/subprocessor accountability | Document what leaves device in user consent + audit log |
| **OECD Health Data Governance (2025)** | Purpose binding, transparency | Manifest names issuer, TTL, scopes; tools enumerated |
| **ONC / PGHD guidance** | Patient-generated data as *signals*, not raw dump | Clinical summary + FHIR subset, not Omi archive |

Contracts should be **inspectable** (YAML/JSON the user can read) and **enforceable in code** (not PDF-only).

## 2. Patterns from products & protocols (examples)

### A. Local-first with optional cloud enrichment

- **Apple Health (on-device analysis narrative, 2025+):** Analysis stays on device; cloud features are opt-in and scoped — aligns with “core local, boost optional.”
- **FHIR Consent / Provenance resources:** Machine-readable consent scope + who asserted it — maps to future `doctor-issuer-attestation` + signed manifest.
- **Research N-of-1 / single-subject trials:** Export **binned metrics + event dates**, not full diaries — matches `_sanitize_correlations` / top-5 caps.

### B. Agent / tool contracts

- **MCP tool surface:** Explicit tool list in manifest prevents scope creep (sidecar cannot call undeclared tools).
- **Capability attenuation (Macaroons-style, future):** Start from doctor-issued manifest → user cannot widen Azure ops without re-issue — current code: `allowed_operations(manifest)` hard gate.

### C. LLM-specific minimization

- Send **structured stats first**, natural language second (VitaSide already computes correlations locally).
- **Short excerpts** with anonymization (`anonymize_text`, `max_excerpt_chars`) — industry norm for “RAG with citations” without full note upload.
- **No vault paths / filenames** in outbound JSON — prevents indirect identification via folder structure.

## 3. Contract layers (recommended stack)

```
Layer 1: User-owned data (vault, Apple export) — never in contract as outbound
Layer 2: Sidecar manifest (read scopes, TTL, tools)
Layer 3: Operation consent (per call: enhance_insight, share_report, …)
Layer 4: Payload policy (data_minimization block + fingerprint)
Layer 5: Cloud processor terms (Azure DPA, region, retention) — human/legal, referenced in consent template
```

## 4. Anti-patterns to forbid in templates

- “Upload your Health export for better AI”
- Unlimited `allowed_operations: ["*"]`
- Sharing full `.md` conversation files or `export.xml`
- Persistent cloud storage of payloads beyond documented TTL (default **48h** for share links in VitaSide docs)
- Diagnostic claims in consent text (stay observational / visit-prep)

## 5. Verification hooks (already in repo)

```bash
cd code/health-mcp-starter
export VITASIDE_MANIFEST=sidecars/azure-hybrid-sidecar/manifest.yaml
python3 -c "
from azure_contract import build_payload, validate_outbound, contract_info
from sidecar_protocol import load_manifest
m = load_manifest('sidecars/azure-hybrid-sidecar/manifest.yaml')
info = contract_info(m)
assert info['azure_enabled']
print('ops', info['allowed_operations'])
"
```

Use `preview_azure_payload` MCP tool before any live `VITASIDE_AZURE_MODE=live` trial.

## 6. Related vault / docs

- [[azure-minimal-exposure-matrix]] — Azure feature checklist
- `docs/MCP-SIDECAR-TECHNICAL-SURVEY.md` §4 Privacy Contracts
- `docs/VIT-4-AZURE-HEALTH-EVALUATION.md` — service map + schema examples