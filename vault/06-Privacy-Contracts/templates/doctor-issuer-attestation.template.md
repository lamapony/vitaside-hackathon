# Doctor / issuer attestation (template)

**Sidecar name:** `{{sidecar_name}}`  
**Issued to patient device:** `{{patient_label}}` (pseudonym ok)  
**Issuer:** `{{issuer_name}}` · **Credential:** `{{issuer_role}}`  
**Date (UTC):** `{{issued_at}}` · **TTL:** `{{ttl}}`

## I attest that

1. This sidecar is issued for **self-observation and visit preparation**, not autonomous diagnosis or treatment.
2. **Read scopes** in the manifest are limited to paths the patient approved:
   - `{{scope_summary}}`
3. **Azure cloud boost** is `{{azure_enabled}}`. If enabled, only these operations are allowed:
   - `{{allowed_operations}}`
4. I directed the patient to review [[templates/azure-user-consent.template]] before any live cloud call.
5. I understand VitaSide logs **tool names and payload fingerprints**, not raw note text, in local `audit.log`.

## Data minimization profile

| Setting | Value |
|---------|-------|
| `max_excerpt_chars` | {{max_excerpt_chars}} |
| `anonymize_by_default` | {{anonymize_by_default}} |

## Revocation

Patient may revoke at any time via `revoke-sidecar.sh`. Issuer should document revocation in clinical record if visit prep was abandoned.

---

*Future:* cryptographic signature over manifest hash (not required for hackathon MVP).

**References:** [[VIT-9-best-practices]] · `docs/AZURE-CONTRACT.md`