# VitaSide Hackathon - Detailed Implementation Plan

**Inspired by:** https://github.com/addyosmani/agent-skills (structured engineering skills for AI agents: /spec, /plan, /build, /test, /review, /ship with quality gates).

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