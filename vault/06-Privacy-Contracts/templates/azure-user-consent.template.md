# Azure boost — user consent (template)

**Sidecar:** `{{sidecar_name}}` · **Issuer:** `{{issuer}}` · **Expires:** `{{ttl_end}}`

Before VitaSide sends anything to Microsoft Azure, confirm you understand:

## What stays on your device

- Full Omi transcripts and journal files
- Apple Health `export.xml` (if linked)
- File paths and folder names
- Photos (unless you separately consent to skin observation tools)

## What may be sent (only if you enable Azure and call a cloud tool)

| Operation | Contents |
|-----------|----------|
| `enhance_insight` | Day counts, signal tallies, up to **{{max_excerpt_chars}}** characters per cited quote (anonymized: **{{anonymize}}**), top pattern summaries |
| `share_report` | Same minimized JSON as preview; stored behind a **time-limited link** (default **48 hours**) |

VitaSide will show a **preview** (`preview_azure_payload`) before the first live send.

## Your choices

- [ ] I enable Azure boost for this sidecar (`enable_azure_boost: true` in manifest)
- [ ] I consent to operation: `________________` on `________________` (UTC)
- [ ] I have read [[azure-minimal-exposure-matrix]] and accept residual risk of short excerpts

## What VitaSide does not do

- No diagnosis or treatment decisions
- No automatic upload to your clinic/EHR
- No sale of your data

**Revoke:** `./revoke-sidecar.sh {{sidecar_name}}` · **Audit:** `audit.log` (fingerprints only)

---

*Processor:* Microsoft Azure services per [[azure-minimal-exposure-matrix]] · *Controller for outbound decision:* you (the device owner).