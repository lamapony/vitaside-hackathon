# Sidecar Manifest Open Standard (Draft)

**Status:** Draft (VitaSide reference implementation)  
**Issue:** VIT-38 · **Prep adjustment:** #4 — formalize Sidecar Manifest protocol  
**Agent:** Systems Architect  
**Date:** 2026-06-28  
**Normative keywords:** The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** in this document are to be interpreted as described in RFC 2119.

**Related:** [[ADR-001-mcp-sidecar-for-personal-health|ADR-001]], [[../06-Privacy-Contracts/_index|06-Privacy-Contracts]], hackathon `sidecar_protocol.py`

---

## 1. Purpose

A **sidecar manifest** is a human-readable contract between an **issuer** (clinician, coach, or self) and a **host agent** (e.g. Hermes) that defines:

- Which filesystem paths the sidecar MAY read  
- Which MCP tools the sidecar MAY expose  
- How long the delegation remains valid (**TTL**)  
- Output **quality gates** for health-adjacent insights  
- How **audit** events are recorded  

This draft standard aligns with the VitaSide hackathon reference implementation so other MCP hosts can adopt the same YAML shape without forking governance logic.

---

## 2. Document format

- Encoding: UTF-8  
- Syntax: YAML 1.2 (JSON-compatible subset permitted for tooling)  
- File name: `manifest.yaml` inside `sidecars/<sidecar-id>/`  
- Environment variables in `path` or `server.args` MAY be expanded at **issue time** by the issuer script; committed public examples MUST use demo paths or placeholders (`${OMI_VAULT_PATH}`).

---

## 3. Top-level field reference

| Field | Required | Type | Semantics |
|-------|----------|------|-----------|
| `name` | **MUST** | string | Stable sidecar identifier (kebab-case recommended). |
| `version` | **MUST** | string | Manifest schema / pack version (semver or `0.1`). |
| `description` | SHOULD | string | Human summary for issuer and patient. |
| `issuer` | **MUST** | string | Email, URI, or `patient-self` — who asserted the contract. |
| `ttl` | **MUST** | string | Lifetime; see §4. |
| `issued_at` | **MUST** | string | ISO-8601 UTC timestamp when issued. |
| `allowed_scopes` | SHOULD | list | Empty list = dev-only permissive mode in reference impl; production SHOULD list scopes. |
| `tools` | **MUST** | list of strings | MCP tool allow-list; see §6. |
| `quality_gates` | **MUST** | list of strings | Output constraints; see §7. |
| `server` | **MUST** | object | MCP host launch spec; see §10. |
| `enable_azure_boost` | MAY | boolean | Default **false** if omitted (privacy-first). |
| `azure` | MAY | object | Cloud minimization contract; see §9. |
| `condition_pack` | MAY | string | Condition specialization id (e.g. `migraine`). |
| `revoked_at` | MAY | string | Set by revocation; sidecar MUST NOT run after this. |

Implementations MAY add extension fields if hosts ignore unknown keys.

---

## 4. TTL (time-to-live)

The `ttl` field defines when the sidecar **expires** relative to `issued_at`.

**Normative parsing (VitaSide reference):**

1. If `ttl` ends with `d`, value is integer days added to `issued_at`.  
2. If `ttl` ends with `h`, value is integer hours added to `issued_at`.  
3. Else if `ttl` is ISO-8601 datetime, that instant is the expiry.  
4. Else implementations SHOULD default to **30 days** from `issued_at` and log a warning.

On each tool invocation the sidecar **MUST**:

- Reject if `now > expires_at` (event: `sidecar_expired`).  
- Reject if `revoked_at` is set (event: `sidecar_revoked_access`).

**Example values:** `"7d"`, `"30d"`, `"72h"`, `"2026-07-28T00:00:00Z"`

---

## 5. `allowed_scopes`

Each scope entry **MUST** be an object:

```yaml
allowed_scopes:
  - path: "/absolute/or/expanded/path/to/vault/root"
    permissions: ["read"]
```

| Subfield | Required | Notes |
|----------|----------|-------|
| `path` | **MUST** | Directory or file root; tilde and env vars expanded by implementation. |
| `permissions` | **MUST** | VitaSide v0.1 supports only **`read`**. Write-back to vault MUST NOT be implied by scope. |

**Enforcement:** Before reading user data, implementation **MUST** resolve the target path and verify it is equal to or under an allowed root (`check_scope`). If `allowed_scopes` is empty, reference implementation allows all paths (**SHOULD NOT** be used in production manifests).

---

## 6. `tools` (MCP allow-list)

- List of MCP tool names the sidecar process registers.  
- Host agents **SHOULD** treat manifests as authoritative: undeclared tools MUST NOT be callable.  
- Reference implementation: `assert_tool_allowed` raises and logs `tool_denied` if violated.

**Core VitaSide tools (non-exhaustive):** `analyze_lifestyle_patterns`, `find_correlation`, `simulate_whatif`, `generate_doctor_report`, `list_data_sources`, `build_visit_packet`, `generate_visit_questions`, `health_check`, `get_azure_contract`, `preview_azure_payload`, condition-pack tools, Azure boost tools when enabled.

---

## 7. `quality_gates`

Gates are **declarative** requirements on tool outputs (enforced in narrative/report code paths).

| Gate id | Meaning |
|---------|---------|
| `always_include_confidence` | Structured confidence on insights. |
| `always_cite_sources` | Dated excerpts or signal references. |
| `include_disclaimer` | Non-diagnostic / not medical advice disclaimer. |

Manifests **MUST** include all three for health-adjacent sidecars. Implementations MAY add gates; hosts SHOULD surface unknown gates in UI for issuer review.

---

## 8. Audit

### 8.1 Log location

- Default path: `audit.log` next to sidecar runtime, overridable via `VITASIDE_AUDIT_LOG`.  
- Format: **append-only JSON Lines** (one object per line).

### 8.2 Required events (reference implementation)

| Event | When |
|-------|------|
| `tool_denied` | Tool not in manifest allow-list. |
| `sidecar_expired` | TTL exceeded on use. |
| `sidecar_revoked` | Manifest written with `revoked_at`. |
| `sidecar_revoked_access` | Use after revocation. |
| Tool-specific rows | Include `tool`, optional `files` (paths or fingerprints), **no raw PHI** in log by default. |

Each row **MUST** include `ts` (ISO-8601 UTC) and `event`.

### 8.3 Host obligations

Hosts **SHOULD** expose `audit_summary` to the user before doctor export and **SHOULD NOT** disable audit for issued clinical sidecars.

---

## 9. Optional Azure block

When `enable_azure_boost: true`:

```yaml
enable_azure_boost: true
azure:
  allowed_operations:
    - enhance_insight
    - share_report
  data_policy:
    max_excerpt_chars: 140
    anonymize_by_default: true
    include_signal_counts: true
    include_whatif: false
```

- `allowed_operations` **MUST NOT** contain wildcards.  
- Outbound payloads **MUST** respect `data_policy` (see `azure_contract.py`).  
- If `enable_azure_boost` is false or omitted, Azure tools **MUST** remain stubbed or denied.

---

## 10. `server` (MCP launch)

```yaml
server:
  command: python3
  args: ["/path/to/health-pattern-mcp.py"]
```

- `command` **MUST** be executable on the host OS.  
- `args` **MUST** include entrypoint script; env `VITASIDE_MANIFEST` **SHOULD** point to this manifest path.  
- Transport **MUST** be MCP over stdio for VitaSide-compatible hosts.

---

## 11. Lifecycle

| Action | Behavior |
|--------|----------|
| **Issue** | Issuer writes manifest, sets `issued_at`, computes TTL, registers in host `mcp_servers`. |
| **Run** | `assert_sidecar_active(manifest, tool=...)` on each tool call. |
| **Expire** | Automatic; no host config change required — process rejects calls. |
| **Revoke** | Issuer or user sets `revoked_at` in YAML (reference: `revoke_manifest()`). |

---

## 12. Hackathon reference manifests

Canonical examples in the hackathon repo (paths relative to `vitaside-hackathon/code/health-mcp-starter/`):

| Sidecar | Path | Notes |
|---------|------|-------|
| Sleep / stress demo | `sidecars/sleep-stress-sidecar/manifest.yaml` | Full visit-prep tool set, local-only |
| Azure hybrid | `sidecars/azure-hybrid-sidecar/manifest.yaml` | `enable_azure_boost: true`, minimization policy |
| Migraine pack | `sidecars/migraine-tracking-sidecar/manifest.yaml` | `condition_pack: migraine` |
| Recovery | `sidecars/recovery-sidecar/manifest.yaml` | Condition specialization |
| Bipolar monitoring | `sidecars/bipolar-monitoring-sidecar/manifest.yaml` | Condition specialization |

Template for new issuers: `vault/06-Privacy-Contracts/templates/sidecar-scope.template.yaml`

**Reference code:** `sidecar_protocol.py` — `load_manifest`, `check_scope`, `assert_sidecar_active`, `audit`, `revoke_manifest`.

---

## 13. Minimal conforming example

```yaml
name: "visit-prep-sidecar"
version: "0.1"
description: "Seven-day cited timeline for PCP visit"
issuer: "patient-self@example.com"
ttl: "7d"
issued_at: "2026-06-28T12:00:00Z"

allowed_scopes:
  - path: "${OMI_VAULT_PATH}/050 Daily Omi"
    permissions: ["read"]

tools:
  - analyze_lifestyle_patterns
  - generate_doctor_report
  - build_visit_packet
  - list_data_sources

quality_gates:
  - always_include_confidence
  - always_cite_sources
  - include_disclaimer

enable_azure_boost: false

server:
  command: python3
  args: ["${VITASIDE_MCP_ENTRY}/health-pattern-mcp.py"]
```

---

## 14. JSON Schema (draft)

For CI validation (optional):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://vitaside.local/schemas/sidecar-manifest-0.1.json",
  "type": "object",
  "required": ["name", "version", "issuer", "ttl", "issued_at", "tools", "quality_gates", "server"],
  "properties": {
    "name": { "type": "string", "minLength": 1 },
    "version": { "type": "string" },
    "issuer": { "type": "string" },
    "ttl": { "type": "string" },
    "issued_at": { "type": "string", "format": "date-time" },
    "allowed_scopes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["path", "permissions"],
        "properties": {
          "path": { "type": "string" },
          "permissions": { "type": "array", "items": { "enum": ["read"] } }
        }
      }
    },
    "tools": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
    "quality_gates": {
      "type": "array",
      "items": {
        "enum": [
          "always_include_confidence",
          "always_cite_sources",
          "include_disclaimer"
        ]
      },
      "minItems": 1
    },
    "enable_azure_boost": { "type": "boolean", "default": false },
    "revoked_at": { "type": "string", "format": "date-time" }
  }
}
```

---

## 15. Verification (reference implementation)

```bash
cd code/health-mcp-starter
export VITASIDE_MANIFEST=sidecars/sleep-stress-sidecar/manifest.yaml
python3 -c "
from sidecar_protocol import load_manifest, assert_sidecar_active
m = load_manifest()
assert_sidecar_active(m, tool='list_data_sources')
print('ok', m['name'], m['_expires_at'])
"
```

---

## 16. Open questions (v0.2)

- Cryptographic signature over manifest hash (`doctor-issuer-attestation` template).  
- Portable vault root indirection (`vault_root_id` vs absolute paths).  
- Standard `escalation_policy` field (no auto-alert to EHR).  
- Cross-host manifest discovery URI.

---

*Proof: VIT-38 — saved to VitaSide-Research vault 2026-06-28.*