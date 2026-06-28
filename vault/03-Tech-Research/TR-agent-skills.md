# TR — Agent skills frameworks

## What “agent skills” means (2025–2026)

- Packaged workflows: **when to use**, **steps**, **quality gates**, **tools** — e.g. [agent-skills](https://github.com/addyosmani/agent-skills) lifecycle: `/spec`, `/plan`, `/build`, `/test`, `/review`, `/ship`.
- Hermes: `skills/` directory, `skill_view`, profile-scoped plugins.
- Cursor/Codex: rules + task prompts for specialized agents (UI agent in `plan/UI-AGENT-PROMPT.md`).

## Adoption signal

- Multi-agent hackathon projects split **research / architect / UI / Azure** with file ownership (`plan/ORCHESTRATION.md`) — same idea as skills.
- Reduces hallucination in health if skills **require citations and test commands**.

## VitaSide today

- `plan/README.md` explicitly maps to agent-skills lifecycle ✅
- Missing: single **HealthPatternSkill** entry point (“parse → analyze → report → handoff”) invocable from Hermes.

## Recommendation

1. Add `skills/health-pattern/` (or Hermes profile skill) with steps mirroring `test_mvp.py` gates.
2. Pair agent VIT-13 competitor survey with skill “compare_to_incumbent” template.