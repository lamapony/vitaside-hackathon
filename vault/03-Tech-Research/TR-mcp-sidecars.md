# TR — MCP protocol & sidecars in agents

## State of MCP (2025–2026)

- **Model Context Protocol** is the common **tool discovery + invocation** layer for AI clients (desktop agents, IDEs, research agents).
- Typical deployment: **stdio** for local servers; **HTTP+OAuth** for remote hosted tools (enterprise connectors).
- Ecosystem growth: large catalog of reference servers; health-specific servers remain **niche** — opportunity for VitaSide as **reference health sidecar**.

## Sidecar pattern (agent architecture)

| Property | Why it matters for health |
|----------|---------------------------|
| **TTL / expiry** | Doctor-issued or self-issued limited access |
| **Scoped paths** | Read only Omi + Apple export dirs |
| **Tool allowlist** | No arbitrary shell on vault |
| **Audit trail** | Trust + debugging |

## VitaSide alignment

**Strong match** — implemented: `sidecar_protocol.py`, YAML manifests, `audit.log`, FastMCP stdio (`docs/MCP-SIDECAR-TECHNICAL-SURVEY.md` VIT-3).

## Gaps vs market maturity

1. **Remote MCP** not required for hackathon; defer HTTP transport.
2. **OAuth identity** for “clinic-issued sidecar” — future; keep manifest `issuer` field.
3. **Hermes production delegation** still backlog (`plan/README.md` item 4) — highest integration priority.

## Recommendation

- Stay **MCP + stdio**; extend manifest with `data_minimization_level` and `escalation_policy` (see [[PP-08-who-acts-on-anomaly]]).
- Publish **mcporter / Hermes config snippet** as onboarding skill.