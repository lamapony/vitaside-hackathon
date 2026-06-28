# TR — Local-first privacy in health apps

## Trends

- **On-device** processing for health metrics (OS vendors) sets user expectation: “my phone already does local.”
- **Data minimization** contracts for any cloud LLM step (aggregates only, no raw transcript) — matches GDPR-minded EU users (Copenhagen context).
- Breach fatigue → **default deny outbound** is a selling point, not a limitation.

## Patterns that work

| Pattern | Example use |
|---------|-------------|
| Local compute + optional cloud narrative | VitaSide `azure_contract.py` |
| User-controlled export | HTML/MD/FHIR bundle on demand |
| Append-only audit | `audit.log` |
| No write-back to vault | Prevents silent mutation of medical notes |

## Risks if we drift cloud-first

- Lose trust positioning vs Apple Health + notes workflow.
- Hackathon judges may ask “where does data go?” — local answer must be **one sentence + log proof**.

## Recommendation

- UI: **“Cloud boost off”** as default badge.
- Document **exact payload shapes** in `schemas/azure-payload-*.example.json` for reviewers.