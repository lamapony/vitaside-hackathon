# VIT-4: Azure integrations & health data sources (data minimization)

**Issue:** Map Azure services under strict controls; research Apple/Google Health local exports and wearables; prototype contract examples.

**Status:** Complete (code + schemas + catalog). Live Azure credentials remain post-hackathon backlog.

---

## 1. Azure services map (strict controls)

Enforced in `azure_contract.py` → `AZURE_SERVICES` + `build_payload()` + `validate_outbound()`.

| Key | Service | Allowed payload | Controls |
|-----|---------|-----------------|----------|
| `storage` | Azure Blob | Minimized `share_report` JSON only | TTL/SAS, encryption at rest, no raw exports |
| `ai` | Azure OpenAI | `enhance_insight` aggregates + trimmed excerpts | Private endpoint, content filters, MI over keys |
| `functions` | Azure Functions | Same as share payload | Stateless, 48h TTL default, ingress audit |
| `search` | Azure AI Search | Embeddings + query id (future) | No full note text unless explicit consent |
| `health` | Health Data Services (FHIR) | Visit bundle subset | Pseudonymized patient id, no full history |

**Never outbound:** vault paths, full Omi transcripts, Apple `export.xml`, Google Takeout archives.

---

## 2. Local health & wearable sources

| Source | Format | Discovery | Wearable metrics | Privacy |
|--------|--------|-----------|------------------|---------|
| **Apple Health** | Single `export.xml` (Health app export) | `~/Downloads/apple_health_export/`, vault `Apple Health/` | sleep_hours, HRV, steps, HR | `local_only` — `apple_merge.py` |
| **Google Fit / Health Connect** | Fragmented JSON/CSV/Takeout zip | `~/Downloads/google_health_export/`, `Fit/` | steps, HR, sleep, activity minutes | `local_only` — catalog + `find_google_export()` (parser TBD) |
| **Omi vault** | Markdown in Obsidian | `OMI_VAULT_PATH`, scoped manifest | Subjective signals (sleep, stress, mood) | `local_only` |
| **Manual log** | `local-data/user_context.json` | Dashboard / API | Headache severity, meds | `local_only` |

**Wearables research note:** Apple provides one canonical XML; Google has no single file — Takeout (Fit) and Health Connect export apps are the practical paths. Third-party exporters (e.g. structured JSON) are acceptable if user places files under documented search paths.

---

## 3. Prototype contract examples (all operations)

| Operation | Example JSON |
|-----------|----------------|
| `enhance_insight` | `code/health-mcp-starter/schemas/azure-payload-v1.example.json` |
| `share_report` | `code/health-mcp-starter/schemas/azure-payload-share-report.example.json` |
| `fhir_export` | `code/health-mcp-starter/schemas/azure-payload-fhir.example.json` |
| Data sources API shape | `code/health-mcp-starter/schemas/data-sources.example.json` |

Manifest gate (required for any cloud op):

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

## 4. Verification commands

```bash
cd code/health-mcp-starter
./issue-sidecar.sh azure-hybrid-sidecar
export VITASIDE_MANIFEST=sidecars/azure-hybrid-sidecar/manifest.yaml
python3 test_mvp.py
python3 -c "from azure_contract import contract_info; from sidecar_protocol import load_manifest; m=load_manifest('sidecars/azure-hybrid-sidecar/manifest.yaml'); print(list(contract_info(m)['azure_services'].keys()))"
python3 -c "from data_sources import SOURCE_CATALOG; print([s['id'] for s in SOURCE_CATALOG if s['id'] in ('apple_health','google_health','azure_boost')])"
```

---

## 5. Related docs

- `docs/AZURE-CONTRACT.md` — tool surface + env checklist
- `docs/azure-hybrid-options.md` — product/architecture options
- `docs/MCP-SIDECAR-TECHNICAL-SURVEY.md` — privacy contracts survey (VIT-3)