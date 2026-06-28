# TR — VitaSide impact analysis (VIT-12)

## Current vision (unchanged core)

Personal pattern intelligence · local MCP sidecar · Omi + Apple + journals · visit prep · non-diagnostic · citations + confidence.

**Code reality (2026-06-27):** MVP shipped per `plan/README.md` — 30+ tools, UI, clinical summary, N-of-1, FHIR export, Azure contract stub.

## Research vs plan — alignment matrix

| Research theme | Plan / code | Alignment | Suggested shift |
|----------------|-------------|-----------|-----------------|
| Visit prep / PGHD binning | `clinical_summary`, doctor HTML | ✅ High | **Priority:** PDF print, pre-visit ritual in Prep-Phase |
| MCP sidecars | `sidecar_protocol`, FastMCP | ✅ High | Ship Hermes live delegation |
| Local-first | Azure minimization contract | ✅ High | Marketing + UI default-off cloud |
| N-of-1 science | `n1_compare`, lag p-values | ✅ Medium-high | Surface FDR/regime in UI (DEPTH-SPRINT remainder) |
| Agent skills | plan lifecycle docs | 🟡 Medium | Formal HealthPatternSkill |
| Competitor clarity | — | ⚪ Low | **VIT-13** → `02-Existing-Solutions/` |
| Population ML / heavy Azure | DEPTH optional | 🟡 Low priority | **De-emphasize** for next 2 sprints |

## Recommended course corrections (priority order)

1. **Product narrative:** “3-minute doctor handoff from your vault” over “AI health assistant.”
2. **Integration:** Hermes production MCP path (not demo script only).
3. **Trust artifacts:** audit log + scope summary in every report footer.
4. **Parser quality:** gate high-confidence insights on Omi quality score (UI).
5. **Human loop:** real 30–60 day vault on Dima’s data (`plan/README` backlog #1).
6. **Defer:** remote MCP OAuth, AutoML on Azure, vector RAG on full notes (unless opt-in research).

## Opportunities to double down

- **Doctor-issued manifest** story for hackathon pitch (TTL + scopes).
- **FHIR export** as “system-ready” without sending raw stream.
- **Sidecar specialization** packs (sleep-stress, recovery) already in `sidecars/` — demo switching manifests.

## Proposed next development steps

See [[../Prep-Phase-Plan#Next development steps (post VIT-12)|Prep-Phase-Plan — Next steps]].