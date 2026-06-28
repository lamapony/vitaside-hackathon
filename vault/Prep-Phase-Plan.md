# Prep Phase Plan — VitaSide

> **Owner:** Lead Researcher (VIT-12)  
> **Updated:** 2026-06-28  
> **Vault:** `vitaside-hackathon/vault/`

## Purpose

Prepare product and engineering direction **before** the next depth sprint: pains documented, tech landscape scanned (30-day emphasis), gaps vs MVP explicit.

## Phase checklist

| Step | Status | Artifact |
|------|--------|----------|
| Pain point cards | ✅ | [[01-Pain-Points/_index]] |
| Tech research (4 themes) | ✅ | [[03-Tech-Research/_index]] |
| Impact vs current plan | ✅ | [[03-Tech-Research/TR-vitaside-impact]] |
| Existing solutions survey | 🔲 | **VIT-13** → `02-Existing-Solutions/` (not started) |
| Real data on founder vault | 🔲 | Human: `OMI_VAULT_PATH` + Apple export |

## Findings summary (VIT-12)

### Pains that matter most

1. [[01-Pain-Points/PP-01-recall-at-visit]] — primary user job-to-be-done.
2. [[01-Pain-Points/PP-03-pghd-fatigue]] — why clinical summary must stay short.
3. [[01-Pain-Points/PP-04-trust-cloud-health-ai]] — why local MCP is the wedge.

### Tech conclusions

- **MCP stdio sidecar** remains correct architecture ([[03-Tech-Research/TR-mcp-sidecars]]).
- **Local-first** is market-aligned, not retro ([[03-Tech-Research/TR-local-first-privacy]]).
- **Agent skills** lifecycle already in `plan/`; add executable HealthPatternSkill ([[03-Tech-Research/TR-agent-skills]]).

### Vision validation

Current VitaSide vision **does not need a pivot**. Narrower **go-to-market emphasis**:

> *Cited personal timelines → visit-ready handoff → optional FHIR bundle; runs in your agent; data stays local.*

## Course corrections (approved for planning)

| Change | Type | Rationale |
|--------|------|-----------|
| Lead with doctor handoff | Positioning | Matches PGHD/clinical fatigue research |
| Hermes live delegation | Engineering P1 | MCP adoption is agent-native, not standalone app |
| PDF / print doctor bundle | Engineering P2 | PP-01 recall pain at physical visit |
| Parser quality in UI | Engineering P2 | PP-05 noisy Omi |
| Cloud boost default off | UX + trust | PP-04 |
| Push VIT-13 competitor table | Research | Closes positioning vs Apple/portals/trackers |

**No shift:** away from non-diagnostic stance, N-of-1 stats core, or temporary scoped sidecars.

## Next development steps (post VIT-12)

**Sprint A — Trust + visit (1–2 weeks)**

1. PDF or print-optimized CSS for doctor report.
2. Report footer: audit summary + disclaimer + data scope.
3. Document “24h before visit” checklist in README / skill.

**Sprint B — Agent integration (1 week)**

4. Hermes `mcp_servers` production config + smoke test (not `collaboration_demo.py` only).
5. Publish HealthPatternSkill with gates from `python3 test_mvp.py`.

**Sprint C — Evidence loop (ongoing)**

6. Founder 30-day journal + retrospective (DEPTH-SPRINT human metric).
7. VIT-13: `vault/02-Existing-Solutions/_index.md` + 5–8 tool notes linked to PP-* cards.

**Backlog unchanged** (from `plan/README.md`): Azure live, large vault perf, regime/FDR UI polish.

## Links to repo docs

- `plan/README.md` — code reality snapshot
- `docs/MCP-SIDECAR-TECHNICAL-SURVEY.md` — VIT-3 architecture
- `plan/DEPTH-SPRINT.md` — clinical/PGHD trends table
- `docs/AZURE-CONTRACT.md` — hybrid minimization

## Paperclip

- **VIT-12:** this prep phase research — **complete** when vault + this file land.
- **VIT-13:** assign next for competitor deep dive.