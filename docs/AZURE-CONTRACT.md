# VitaSide ↔ Azure Integration Contract v1.0

**Audience:** Azure integration agent (second workstream).  
**Principle:** Local MCP owns all raw data. Azure receives **minimized, consented payloads only**.

---

## Architecture

```
User machine (Hermes + VitaSide MCP)
  • parse Omi / Apple (local)
  • patterns, condition packs (local)
  • azure_contract.build_payload()
        │
        │ HTTPS (opt-in, audited)
        ▼
Azure (second agent)
  • OpenAI: enhance_insight
  • Function + Blob: share_report
  • AI Search: embed_search (future)
  • FHIR: fhir_export (future)
```

**Core works without Azure.** `VITASIDE_AZURE_MODE=stub` (default) returns local fallback text.

---

## Manifest flags

```bash
./issue-sidecar.sh azure-hybrid-sidecar
```

```yaml
enable_azure_boost: true
azure:
  allowed_operations:
    - enhance_insight
    - share_report
  data_policy:
    max_excerpt_chars: 140
    anonymize_by_default: true
```

---

## MCP tools (local)

| Tool | Purpose |
|------|---------|
| `get_azure_contract()` | Contract version, enabled ops, env checklist |
| `preview_azure_payload(operation, user_consent, anonymize)` | Dry run — JSON that would leave the device |
| `azure_enhance_insight(user_consent=True, …)` | Payload → `azure_boost.enhance_insight()` |
| `azure_share_report(user_consent=True, ttl_hours=48, …)` | Payload → share stub / Function |

`user_consent=True` is required for live calls. Audit log records `azure_*` + payload fingerprint.

---

## Operations

### `enhance_insight`

**Env:** `VITASIDE_AZURE_MODE=live`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_KEY` (or Managed Identity).

**Implement in:** `azure_boost._call_openai()`

### `share_report`

**Env:** `AZURE_FUNCTION_SHARE_URL`

**Implement in:** `azure_boost._call_share_function()` + Azure Function repo

---

## Payload example

`code/health-mcp-starter/schemas/azure-payload-v1.example.json`

**Never include:** vault paths, full transcripts, Apple XML.

---

## Python modules

| Module | Role |
|--------|------|
| `azure_contract.py` | Payload builder, validation |
| `azure_boost.py` | **Azure agent extends** — HTTP, stub/live |
| `health-pattern-mcp.py` | Thin MCP wrappers only |

---

## Demo (stub)

```bash
cd code/health-mcp-starter
./issue-sidecar.sh azure-hybrid-sidecar
export VITASIDE_MANIFEST=sidecars/azure-hybrid-sidecar/manifest.yaml
python3 test_mvp.py
```
