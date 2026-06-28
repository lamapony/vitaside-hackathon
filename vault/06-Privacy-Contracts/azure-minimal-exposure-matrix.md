# Azure hybrid — minimal exposure control matrix (VIT-9)

Maps **VitaSide operations** (`azure_contract.OPERATIONS`) to **Azure features** that reduce blast radius if a payload or key leaks.

**Rule:** Raw PGHD never leaves the laptop. Cloud sees only `build_payload()` output after `validate_outbound()`.

## Summary table

| Operation | Azure service | Data that may leave device | Minimal-exposure controls (prioritized) |
|-----------|---------------|----------------------------|----------------------------------------|
| `enhance_insight` | Azure OpenAI | Aggregates, top insights, ≤140 char excerpts | Private Endpoint; **Managed Identity**; deployment in chosen region; content filters + abuse monitoring; **no** vault paths in prompt; disable training on customer data (enterprise/DPA); prompt logging off where offered |
| `share_report` | Azure Functions + Blob | Same minimized JSON as preview | HTTPS only; Function **auth level** function/key in Key Vault; Blob **SAS TTL** (≤48h); encryption at rest (CMK optional); lifecycle rule auto-delete; ingress logging without body retention |
| `embed_search` (future) | Azure AI Search | Embedding vectors + doc ids | Separate index per user/pilot; no raw text index unless explicit consent; RBAC + Private Link |
| `fhir_export` (future) | Azure Health Data Services | FHIR bundle subset | Dedicated FHIR workspace; pseudonymized `Patient.id`; consent record; audit trail; BAA if US HIPAA path |

## Per-service deep dive

### Azure OpenAI (`ai`)

| Control | Why it matters for VitaSide |
|---------|----------------------------|
| **Private Endpoint** | Traffic never crosses public internet |
| **Managed Identity** | No API keys in `azure_boost.py` or env on disk |
| **Regional deployment** | EU (e.g. Sweden Central) for Copenhagen users |
| **Content filtering** | Blocks accidental PII patterns in model I/O |
| **Input size cap** | `prompt_hint` truncated to 500 chars in payload |
| **Stub default** | `VITASIDE_AZURE_MODE=stub` — zero egress in dev/demo |

**Not recommended for MVP:** Sending images, full chat logs, or Apple XML through OpenAI.

### Azure Functions + Blob (`functions`, `storage`)

| Control | Implementation note |
|---------|---------------------|
| Stateless function | No DB of PHI; generate SAS and return URL |
| Short SAS | Align with `ttl_hours=48` on `azure_share_report` |
| CMK / SSE | Blob encryption; customer-managed keys for pilots |
| Application Insights | Sample **metadata** only (operation, fingerprint), not payload body |

### Azure AI Search (`search`)

| Control | Note |
|---------|------|
| Embeddings-only default | Matches `AZURE_SERVICES.search.data_min` |
| Optional excerpt mode | Requires manifest `data_policy` bump + second consent string |

### Azure Health Data Services (`health`)

| Control | Note |
|---------|------|
| FHIR R4 subset | Use local `fhir_export.py` output, not raw notes |
| Provenance resource | Link bundle to sidecar issuer + payload fingerprint |

## Cross-cutting Azure guardrails

1. **Azure Policy** — deny public blob access; require TLS 1.2+
2. **Key Vault** — secrets, SAS signing keys, Function keys
3. **Microsoft Defender for Cloud** — posture on storage + Functions
4. **Diagnostic settings** — send to locked-down Log Analytics; **scrub** request bodies in custom pipelines
5. **Purview (optional)** — classify any stored JSON as *Personal Health* for retention policies

## Manifest knobs (user/doctor visible)

```yaml
enable_azure_boost: true   # default false for privacy-first demos
azure:
  allowed_operations:
    - enhance_insight      # never use wildcard
  data_policy:
    max_excerpt_chars: 140
    anonymize_by_default: true
    include_signal_counts: true
    include_whatif: false   # tighten for maximum minimization profile
```

## Enforcement in code

| Check | Module |
|-------|--------|
| Operation allow-list | `allowed_operations()`, `build_payload()` |
| Consent | `consent.granted` + MCP `user_consent` param |
| Forbidden tokens | `validate_outbound()` |
| Audit without content | `payload_fingerprint()` in audit log |

## Risk residual (honest)

- Short excerpts may still be identifying in small N-of-1 datasets → default anonymization on.
- Cloud LLM could memorize rare strings → keep excerpts short; prefer stats over quotes when `max_excerpt_chars: 0` (future policy flag).

See templates in `templates/` and examples in `code/health-mcp-starter/schemas/`.