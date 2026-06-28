# TR — Health AI, self-observation, visit preparation (recent)

## What changed recently (2025–2026)

- **PGHD → EHR** pipelines are documented (AHRQ practical guide, HL7 PGHD IG): systems want **structured observations**, not chat logs.
- **Clinical documentation AI** in hospitals is hot; **patient-side** tools that produce **clinic-ready summaries** are under-served vs symptom checkers.
- **Wearables + journals** remain high-volume; the pain is **synthesis with provenance**, not another dashboard.

## Competitor / adjacent patterns (not full survey — see VIT-13)

| Pattern | Strength | Failure vs our pains |
|---------|----------|----------------------|
| Apple Health trends | Local, trusted device | Weak subjective narrative; no visit prep doc |
| Patient portals (MyChart) | Official labs | No lifestyle correlation; no agent |
| Mood trackers | Fast logging | Little lag stats / cite-back |
| Generic health LLM chat | Fluent language | No vault provenance; privacy fear [[PP-04-trust-cloud-health-ai]] |

## Insights for VitaSide

- Position as **“personal PGHD intelligence layer”** — aligns with system trends without claiming diagnosis.
- Lead demo with **doctor handoff + FHIR export stub**, not open-ended chat.
- Emphasize **N-of-1** and **citations** as differentiators vs population-trained wellness bots.

## Sources / anchors

- AHRQ PGHD guide (digital.ahrq.gov)
- HL7 PGHD IG (build.fhir.org)
- npj Digital Medicine sociotechnical PGHD (2025) — cited in `plan/DEPTH-SPRINT.md`
- Internal: `docs/MVP-1.0.md`, `clinical_summary.py`, `fhir_export.py`