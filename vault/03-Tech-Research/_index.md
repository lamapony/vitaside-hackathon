# 03 — Tech Research (VIT-12)

> Window: **2026-05-28 → 2026-06-28** · Issue **VIT-12**
> Companion: [[../01-Pain-Points/_index|01-Pain-Points]] · [[../Prep-Phase-Plan|Prep-Phase-Plan]]

## Index

| Doc | Topic |
|-----|--------|
| [[TR-health-ai-visit-prep]] | Personal health AI, self-observation, doctor prep |
| [[TR-mcp-sidecars]] | MCP in agents, sidecar adoption, governance |
| [[TR-local-first-privacy]] | Local-first / on-device health data |
| [[TR-agent-skills]] | Agent skills frameworks & lifecycle |
| [[TR-vitaside-impact]] | Impact analysis vs current VitaSide plan |
| [[audit-model-differentiator]] | Scoped/temporary/audited model vs MCP security pains (VIT-39) |

## Executive summary (30-day lens)

1. **Health AI** is splitting into (a) **clinical copilots** in EHR, (b) **consumer wellness chat**, and (c) **PGHD summarization** — VitaSide should own **(c) for the patient-owned vault**, not compete with (a)(b).
2. **MCP** is the practical integration layer for personal agents (Hermes, Claude Desktop, IDE agents); **stdio + scoped manifest** matches emerging “tool governance” patterns.
3. **Privacy** narrative favors **default local** + **auditable export**; cloud boost is a **toggle**, not the product.
4. **Agent skills** (spec/plan/build/test) are mainstream for multi-step agent work — VitaSide `plan/` already follows this; formalize a **HealthPatternSkill** for repeatable analysis runs.