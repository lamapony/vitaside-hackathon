# VitaSide Hackathon - Detailed Implementation Plan

**Last synced:** 2026-06-27 · **MVP:** complete · **Entry point for current status:** [`plan/README.md`](README.md)

> **All phases 1–6 below are DONE for hackathon MVP.** The phase descriptions are preserved as historical spec. Post-MVP backlog lives in `plan/DEPTH-ROADMAP.md` and the **Backlog** section of `plan/README.md`.

**Quick proof:** `cd code/health-mcp-starter && python3 test_mvp.py` → ALL MVP CHECKS PASSED.

---

**Project Scope for Hackathon:** Build a working prototype of the VitaSide protocol + compelling live demo using real data. Focus on sidecar issuance, multi-agent collaboration, pattern analysis (extend existing), what-if simulation, beautiful reports. Timebox to hackathon duration (assume 48h sprint).

**Overall Principles (from agent-skills):**
- Spec before code
- Small atomic tasks
- Tests as proof
- Review for quality (no hallucinations in health insights)
- Ship fast but safe
- Always cite data sources, include confidence, audit logs

**Phases (following agent-skills lifecycle):**

## Phase 1: DEFINE / SPEC (What to build - 2-4 hours)
**Goal:** Clear spec before touching code.

**Tasks:**
- Review all inputs in `inputs/` and pitch.
- Write `docs/SPEC.md`: 
  - Protocol definition (simple YAML manifest for sidecar: name, allowed_data_scopes, tools, ttl, version).
  - Sidecar capabilities: analyze_patterns (with lags, anomalies), simulate_whatif, generate_report (markdown/json/html with timeline).
  - Collaboration interface: how main agent delegates to sidecar (e.g., via Hermes tool calls or shared context).
  - Privacy/audit: every access logged, scoped paths only, auto-expire.
  - Demo requirements: end-to-end flow, live on real Omi data, what-if, export.
  - Quality gates: Always return confidence scores, cite exact data excerpts, disclaimers ("patterns only, not diagnosis").
- Define "HealthPatternSkill" following agent-skills pattern: reusable workflow for the sidecar (e.g., steps: 1. Parse data with quality, 2. Compute correlations with stats, 3. Simulate, 4. Format with visuals).
- Success criteria: Spec reviewed and approved (by you).

**Deliverable:** `docs/SPEC.md` + updated pitch if needed.

## Phase 2: PLAN (How to build - 1-2 hours)
**Goal:** Break into small atomic tasks. Use /plan style.

**Tasks:**
- Create `plan/TASKS.md` with numbered, small tasks mapped to phases.
- Prioritize for demo: Core protocol + existing parser extension + what-if + demo UI + multi-agent collab demo.
- Risk mitigation: Data quality (Omi noise) - add quality scoring (already in parser improvements); hallucinations - force citations and confidence.
- Resource: Extend `code/health-mcp-starter/health-pattern-mcp.py` (add tools for simulate, protocol handling).
- For multi-agent: Use Hermes delegation or simple function calls between "main" and "sidecar" in demo script.
- Timeline: Map to hackathon slots (e.g., Day 1 morning spec/plan, afternoon build core, etc.).
- Include agent-skills inspired gates: Every analysis task must include "before/after" or proof.

**Deliverable:** `plan/TASKS.md` (use this as base, expand).

Example tasks structure:
1. [Spec] Finalize protocol manifest format.
2. [Build] Extend MCP server with /simulate_whatif tool using simple stats (pandas).
3. [Build] Add collaboration simulation in demo (main agent queries sidecar).
4. etc.

## Phase 3: BUILD (Incrementally - main time)
**Goal:** One slice at a time. Follow /build.

**Sub-phases:**
- **Core Sidecar Extension (build on existing health-pattern-mcp.py):**
  - Add protocol loader: parse manifest for scopes.
  - Enhance parser (Omi improvements from history: timestamps, context words, speaker separation, quality).
  - Integrate more Apple Health if not full (XML parse for sleep, HR, etc.).
  - Add temporal correlations, anomalies, baseline (pandas/scipy - already partial).
  - New: `simulate_whatif` tool - use historical patterns to project (e.g., regression or simple delta based on past similar periods).
  - MCP sampling if useful: for LLM interpretation of patterns (optional for wow).

- **Collaboration Layer:**
  - In demo, show main agent + sidecar: e.g., Python script simulating "Hermes calls sidecar tool, sidecar responds with data, main adds context".
  - Or use actual Hermes if possible for live.

- **Reports & Visuals:**
  - Enhance generate_doctor_report: support timeline (use matplotlib or ASCII + HTML).
  - Export to Obsidian-style note.
  - Beautiful HTML report with charts (use simple JS or pre-gen).

- **Issuance & Demo Flow:**
  - Script to "issue" sidecar (generate manifest + copy server).
  - Full demo script: issue -> load in "agent" -> run queries -> what-if -> export.
  - Polish existing test-mcporter.sh or add new tests.

**Use agent-skills patterns:**
- For each build slice: write test first (even simple).
- One feature at a time.
- Commit-like checkpoints.

**Deliverable:** Updated `code/health-mcp-starter/` with new features. Working sidecar.

## Phase 4: VERIFY / TEST (Prove it works)
**Goal:** Tests are proof. /test

**Tasks:**
- Extend tests: unit for new parsers/simulate, integration via mcporter.
- Test on real data: run full flow with your Omi vault, capture outputs.
- Edge cases: noisy data, missing Apple, short time ranges.
- Quality gate: every output must have "sources cited", "confidence: X%", disclaimer.
- Demo dry-run: full script runs end-to-end without errors.

**Deliverable:** Passing tests, demo script verified on real data. `code/health-mcp-starter/test-*.sh` updated.

## Phase 5: REVIEW (Improve code health)
**Goal:** /review - audit for quality.

**Tasks:**
- Code review: clean, documented, no magic numbers.
- Performance: analysis <30s on sample data.
- Hallucination prevention: force data-grounded responses.
- Privacy audit: confirm no leaks, scoped.
- Simplify: remove unused from original if any.
- Add docs in code (following agent-skills clarity).

**Deliverable:** Reviewed, cleaned code. Perhaps a `REVIEW.md` notes.

## Phase 6: SHIP (Demo & Pitch ready)
**Goal:** /ship - faster is safer, but polished.

**Tasks:**
- Final demo script + runner (bash/python to simulate full flow).
- Pitch materials: update `pitch/` with slides outline (use pitch deck from agent-skills style? ), demo video script or live.
- README updates, quick start for judges.
- Package: perhaps zip the demo or make it one-command.
- If time: simple web UI for report (static HTML generated).

**Deliverable:** Complete runnable hackathon submission. Pitch ready.

## Timeline Suggestion (for 48h hackathon)
- Hours 1-4: Spec + Plan (this doc)
- Hours 5-20: Build core (parser + simulate + reports)
- Hours 21-30: Collaboration + visuals + tests
- Hours 31-40: Review + polish
- Hours 41-48: Ship, practice demo, final pitch tweaks

**Risks & Mitigations (agent-skills style):**
- Scope creep: Stick to minimal protocol + 3 tools + demo flow.
- Data access: Use your local vault, mock if needed.
- Time: Prioritize demo over perfect code.
- Wow factor: Focus on what-if simulation and multi-agent collab as differentiators.

## How to Execute
Follow agent-skills commands mentally:
- `/spec` -> this plan + SPEC.md
- `/plan` -> break further
- For each task: build, test immediately.
- Use the existing MCP code as base, don't rewrite.

**Success Metrics for Hackathon:**
- Live demo works on real data.
- Judges see novelty (protocol + sidecar collab).
- Clear impact story.
- Technical depth shown (structured skills + MCP + real analysis).

Update this plan as we go. Start with Phase 1.

## Phase 1 Status (2026-06-27) — COMPLETED

All items 6.1–6.6 shipped and verified. Post-audit hardening (same day):

| Item | Status | Location |
|------|--------|----------|
| 6.1 Omi parser (context, speakers, quality, time-of-day) | ✅ | `health-pattern-mcp.py` |
| 6.2 Apple Health XML + merge | ✅ | `apple_merge.py`, `combine_omi_and_apple` |
| 6.3 Temporal correlations, baseline, scipy/pandas | ✅ | `analytics_depth.py`, `smart_analytics.py` |
| 6.4 Reports: HTML timeline, doctor view, Obsidian, visit bundle | ✅ | `report_html.py`, `report_doctor.py`, `export_visit_bundle` |
| 6.5 MCP tools + Azure stub + UI API | ✅ | 30+ tools, `api_server.py`, `azure_contract.py` |
| 6.6 Tests + demo | ✅ | `test_mvp.py` (~56 checks), `run-demo-full.sh --hardening` |

**Bonus shipped (beyond original Phase 1 scope):**
- Local dashboard UI (6 tabs), clinical summary, N-of-1, FHIR export
- Condition packs, journals, headache insights, data sources catalog
- Skin ABCDE observations (rewritten: no `risk_score`, no diagnostic flags)
- Privacy fix: vault path resolution without developer hardcode
- Dependencies: pillow + python-multipart in `requirements.txt`

**Proof:** `test_mvp.py` ALL MVP CHECKS PASSED; `test-mcporter.sh` 15/15 pass.

---

## Phase 2+ (post-hackathon — NOT started as a coordinated phase)

Doctor delivery depth is **partially shipped** (HTML doctor view, clinical summary, FHIR stub). Remaining:

- PDF export
- Real vault + Apple export (human setup)
- Azure live credentials
- Regime detection, FDR in UI (see `plan/DEPTH-SPRINT.md` S3)
- Hermes production delegation

See `plan/DEPTH-ROADMAP.md` for human milestones.

---

## Archived note (original 6.x list)

Code base in `code/health-mcp-starter/` had implemented (confirmed 2026-06-27 morning):

- 6.1 Omi parser: timestamps, context (сегодня/вчера etc), speaker separation, quality scoring, time-of-day - present in health-pattern-mcp.py and supporting.

- 6.2 Apple Health: XML parsing, parse_daily, merge, load_apple_health_data with sleep, HR, activity, symptoms, rings etc.

- 6.3 Temporal correlations (lags 1-3d), anomalies vs baseline, statistical (scipy/pandas) - in analyze_lifestyle_patterns, analytics_depth.

- 6.4 Enhanced reports: JSON, Markdown, HTML with timeline, ASCII charts, visualizations, Obsidian export via export_obsidian.py, visit bundle.

- 6.5 MCP tools + sampling/LLM prep: full MCP server with tools, azure for LLM interpretation (enhance), preview payloads, sampling via context.

- 6.6 Tests: test_mvp.py passes all checks, demo with real demo data, mcporter compatible (test-mcporter.sh), ROADMAP updated.

Azure hybrid added as bonus for usefulness.


