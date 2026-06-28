---
type: tech_research
issue: VIT-39
topic: audit_model_differentiator
skill: source-driven-development
prep_adjustment: 6
updated: 2026-06-28
tags: [mcp, security, audit, sidecar_manifest]
---

# Audit model differentiator (MCP security positioning)

**Issue:** VIT-39 · **Prep adjustment #6** ([[../Prep-Phase-Plan|Prep-Phase-Plan]] / VitaSide-Research `00-Prep-Phase-Plan.md` §7): *Design audit model as differentiator (scoped, temporary, audited tools — solves MCP's top pain).*

**Method:** `source-driven-development` — MCP security pains grounded in ecosystem research + protocol docs; implementation mapping verified against `sidecar_protocol.py` and call sites in `health-pattern-mcp.py`.

**Companion:** [[TR-mcp-sidecars]] · [[TR-local-first-privacy]] · [[../01-Pain-Points/PP-04-trust-cloud-health-ai|PP-04]] · `docs/MCP-SIDECAR-TECHNICAL-SURVEY.md` (VIT-3)

---

## 1. MCP security pains (cited)

Industry adoption outpaced **governance**. Primary sources and vault synthesis:

| Pain | Evidence (source-driven) | Why health / PGHD is acute |
|------|--------------------------|----------------------------|
| **Unbounded tool execution** | MCP hosts discover arbitrary tools; Toloka (2026) frames MCP as expanding attack surface when execution is unopinionated | Omi transcripts + Apple exports are high-sensitivity; one over-broad filesystem tool = full vault read |
| **AuthN / AuthZ gaps** | [MCP specification (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25) defines transports and capabilities; enterprise write-ups stress **session-scoped authorization** as immature vs REST/OAuth stacks | “Who authorized this agent to read my health notes?” has no answer in static `mcp_servers` JSON |
| **Weak observability** | Last-30-days synthesis ([[../../04-research/2026-06-28-last30days-research-vitaside|2026-06-28-last30days-research-vitaside]] §2): observability limitations among six critical MCP challenges; healthcare gateways marketed as fix ([MintMCP healthcare gateways](https://www.mintmcp.com/blog/gateways-healthcare-organizations-with-mcp)) | Compliance asks *what was read, when, by which tool* — not full prompt dumps |
| **Multi-tenant compliance** | Same synthesis §2: HIPAA/GDPR in shared MCP deployments; curated healthcare server lists rate HIPAA posture ([awesome-healthcare-mcp-servers](https://github.com/rdmgator12/awesome-healthcare-mcp-servers)) | Personal N-of-1 data must not inherit “SaaS gateway retention policy” |
| **Registry / trust** | Fragmented server catalogs; users cannot inspect issuance | Patient distrust of cloud health chat ([[../01-Pain-Points/PP-04-trust-cloud-health-ai|PP-04]]) |

**Positioning sentence:** MCP won **interoperability** (97M+ monthly SDK downloads cited in last30days §2); VitaSide wins **issuance + scope + local metadata audit** for personal health analytics — the lagging layer in healthcare MCP deployments.

---

## 2. VitaSide three-part model vs pains

| Control | Mechanism | MCP pain addressed |
|---------|-----------|-------------------|
| **Scoped** | Manifest `allowed_scopes` + `tools[]`; `check_scope()`, `assert_tool_allowed()` | Unbounded tool/path access |
| **Temporary** | `ttl`, `_expires_at`, `revoked_at`; `assert_sidecar_active()` fail-closed | AuthZ without issuance story |
| **Audited** | Append-only JSONL `audit.log` via `audit()` — metadata, paths, fingerprints, counts — **not** raw symptom text in rows | Observability without PHI exfiltration to vendor logs |

Aligned with [[TR-mcp-sidecars]] and ADR-001 pattern: stdio MCP sidecar + declarative manifest, not a central healthcare gateway.

**Differentiator vs generic MCP filesystem server:** purpose-bound **health sidecar** (visit prep, pattern analysis) with `quality_gates` (citations, disclaimer, confidence) in manifest — not “read entire home directory.”

**Differentiator vs cloud health chat:** user inspects **local** `audit.log` and manifest on disk; optional Azure path logs **payload fingerprint** only after `user_consent` (see `preview_azure_payload` / `azure_*` events below).

---

## 3. `sidecar_protocol.py` — core audit API

```117:125:code/health-mcp-starter/sidecar_protocol.py
def audit(event: str, detail: Dict[str, Any]) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "event": event,
        **detail,
    }
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
```

**Governance events (protocol layer)**

| Event | Emitter | Typical `detail` keys | MCP pain mapping |
|-------|---------|----------------------|------------------|
| `tool_denied` | `assert_tool_allowed()` | `tool`, `manifest` | Tool allowlist enforcement |
| `sidecar_expired` | `assert_sidecar_active()` | `manifest` | Temporary access / TTL |
| `sidecar_revoked_access` | `assert_sidecar_active()` | `manifest` | Revocation |
| `sidecar_revoked` | `revoke_manifest()` | `manifest`, `name` | Issuance lifecycle |

**Helpers:** `audit_summary(limit)` aggregates recent rows for report footers (Prep Sprint A item 2).

---

## 4. Runtime events — map to product surface

Events emitted from analytics MCP and adjacent planes (same `audit()` sink; env `VITASIDE_AUDIT_LOG`).

| Event | Source module | User-visible outcome |
|-------|---------------|----------------------|
| `scoped_read` | `health-pattern-mcp.py` (`_scan_omi`) | Omi/journal read under scope; logs `files[]`, `count`, `vault` |
| `smart_analysis` | `health-pattern-mcp.py` | Pattern pass completed; `days` analyzed |
| `personal_baselines` | `health-pattern-mcp.py` | Baseline window; `db_path`, `end_day` |
| `collaborative_insight` | `health-pattern-mcp.py` | Multi-agent context; `events` count |
| `report_export` | `health-pattern-mcp.py` | `format` html \| doctor \| obsidian, `path` |
| `build_visit_packet` | `health-pattern-mcp.py` | Visit prep; `formats`, `questions`, `visit_path`, `entity_id` |
| `get_clinical_summary` | `health-pattern-mcp.py` | Short clinical summary; `trends` count |
| `run_n1_compare` | `health-pattern-mcp.py` | Personal compare window |
| `export_fhir_bundle` | `health-pattern-mcp.py` | Local FHIR bundle path + `entries` |
| `track_condition` / `condition_report` | `health-pattern-mcp.py` | Condition pack lifecycle |
| `list_journals` / `list_data_sources` | `health-pattern-mcp.py` | Discovery without content dump |
| `headache_insights` | `health-pattern-mcp.py` | Pack-specific analytics metadata |
| `analyze_skin_photo` | `health-pattern-mcp.py` | Consent-gated media analysis metadata |
| `health_check` | `health-pattern-mcp.py` | Sidecar status `expired`, `revoked` |
| `preview_azure_payload` | `health-pattern-mcp.py` | Dry-run outbound; `fingerprint`, `consent` |
| `azure_enhance_insight` | `health-pattern-mcp.py` | Cloud boost; `fingerprint`, `mode`, `source` |
| `azure_share_report` | `health-pattern-mcp.py` | Minimized share; `ttl_hours`, `share_url` |
| `azure_embed_search` | `health-pattern-mcp.py` | Embed prototype; `fingerprint` |
| `azure_fhir_export` | `health-pattern-mcp.py` | FHIR cloud stub/live; `fingerprint` |
| `longitudinal_db_denied` | `longitudinal_store.py` | DB path outside manifest scope |
| `path_escape_denied` | `second_brain_scope.py` | Obsidian path outside vault roots |
| `second_brain_read` | `second_brain_scope.py` | Plane B read; scoped note/query metadata |

**Trust demo hook ([[../01-Pain-Points/PP-04-trust-cloud-health-ai|PP-04]]):** After a visit-packet run, show `audit_summary()` → “accessed N scoped files; Azure rows only if `azure_*` events present with fingerprint.”

---

## 5. Comparison matrix (sales / hackathon)

| Approach | Scoped paths + tools | TTL / revoke | Local metadata audit | Cited N-of-1 analytics |
|----------|---------------------|--------------|----------------------|-------------------------|
| Generic MCP + filesystem | Host-dependent | Rare | Rare | No |
| Healthcare MCP gateway | Broker policies | Session | Vendor logs | Varies |
| Cloud health chat | No | N/A | Opaque | Unreliable |
| **VitaSide sidecar** | **YAML manifest** | **`assert_sidecar_active`** | **`audit.log` JSONL** | **Core** |

---

## 6. Limits (honest)

| Limit | Mitigation |
|-------|------------|
| Path scopes are OS-specific | Vault-root indirection in manifest; `OMI_VAULT_PATH` |
| Host can bypass sidecar with raw tools | Hermes delegation + skills; prompt to use VitaSide tools only |
| Unsigned manifests (v1) | Future: issuer attestation ([[../06-Privacy-Contracts/_index|06-Privacy-Contracts]]) |
| Audit UI not shipped | Report footer + `audit_summary` (Prep Sprint A) |

---

## 7. Messaging hooks

1. **“MCP’s missing compliance layer for personal health”** — scoped + temporary + audited as product feature, not slideware.
2. **“Your patterns, your device”** — local-first + audit on same machine (last30days §3).
3. **“Doctor-issued specialist”** — TTL sidecar matches visit-prep on-ramp (adjustment #2).

---

## Proof (VIT-39)

| Check | Result |
|-------|--------|
| Deliverable path | `vault/03-Tech-Research/audit-model-differentiator.md` |
| Protocol events | `tool_denied`, `sidecar_expired`, `sidecar_revoked_access`, `sidecar_revoked` in `code/health-mcp-starter/sidecar_protocol.py` |
| Runtime events | 28 unique audit event names across `health-pattern-mcp.py`, `sidecar_protocol.py`, `longitudinal_store.py`, `second_brain_scope.py` (2026-06-28 verify; includes multiline `audit(` for `build_visit_packet`, `path_escape_denied`) |
| Citations | MCP spec URL + last30days §2–3 + PP-04 + MintMCP/Toloka/awesome-healthcare refs via [[../../04-research/2026-06-28-last30days-research-vitaside]] |

**Related:** [[TR-vitaside-impact]] · `Documents/VitaSide-Research/03-Tech-Research/TR-audit-model-differentiator.md` (VIT-20 mirror; this hackathon vault copy is canonical for VIT-39).