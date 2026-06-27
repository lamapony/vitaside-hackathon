# VitaSide Hackathon Tasks (Atomic, following agent-skills)

Use /plan style: small tasks, one at a time.

## Phase 1: Spec (Done in this plan)
- [x] Create SPEC.md
- [x] Define HealthPatternSkill workflow

## Phase 2: Plan
- [x] Rocket plan: `plan/ROCKET-PLAN.md`

## Build Tasks (Core)
1. Extend MCP server with protocol manifest loader (scopes enforcement).
2. Improve Omi parser (add timestamps, context words like сегодня/вчера, speaker separation, quality scoring) - port from previous work. ✅
3. Add full Apple Health XML support for key metrics (sleep, HR, activity, SpO2). ⚠️ partial
4. Implement temporal correlations (lags), anomalies vs baseline, stats (pandas/scipy). ✅
5. Add `simulate_whatif` tool: based on historical deltas. ✅ Sprint 1
6. Enhance reports: add timeline visualization (HTML with simple charts), citations.
7. Add audit logging for all accesses.
8. Create issuance script (generate manifest + sidecar bundle).
9. Implement demo collaboration simulation (Python script emulating main + sidecar chat).
10. Add quality gates in code: always confidence, sources, disclaimer. ⚠️ partial (analyze + whatif)
11. Demo data generator + run-demo.sh ✅ Sprint 0+1

## Test Tasks
11. Unit tests for new parser functions.
12. Integration test with mcporter for new tools.
13. End-to-end test script on real data, capture outputs for demo.
14. Verify no data leaks, scoped access.

## Review & Polish
15. Code cleanup, docs.
16. Performance check (<30s analysis).
17. Simplify outputs for judges.
18. Create visual assets for pitch.

## Ship
19. Package demo (one-command runner).
20. Final pitch deck / script.
21. Test full demo flow 3x.

Prioritize 1-9 + 13 + 19 for core demo. Use agent-skills: test each slice.

Start with task 1-2.