# VitaSide Protocol Specification (Draft for Hackathon)

**Version:** 0.1 (Hackathon)

## Overview
VitaSide defines a simple protocol for issuing temporary "sidecar" agents that augment a user's main personal AI agent (e.g., Hermes) with specialized capabilities, particularly for health/lifestyle pattern analysis.

The sidecar runs locally, has scoped access, collaborates with the main agent, and expires.

## Core Concepts
- **Sidecar Manifest**: YAML/JSON file describing the sidecar.
- **Sidecar Server**: MCP-compatible server (stdio) implementing the tools.
- **Host Agent**: The main agent (Hermes) that loads the MCP sidecar.
- **Collaboration**: Main agent can call sidecar tools or pass context; sidecar can request additional context from main.

## Sidecar Manifest (Example)
```yaml
name: "sleep-stress-metabolism-sidecar"
version: "0.1"
description: "Analyzes correlations between sleep, activity, stress from voice + biometrics. Supports what-if simulations."
issuer: "doctor@example.com"  # or template
ttl: "30d"  # or ISO date
allowed_scopes:
  - path: "/Users/user/Documents/Obsidian Vault/050 Daily Omi"  # Omi data
    permissions: ["read"]
  - path: "/Users/user/apple-health-export.xml"  # optional
    permissions: ["read"]
tools:
  - analyze_patterns
  - simulate_whatif
  - generate_report
quality_gates:
  - always_include_confidence
  - always_cite_sources
  - include_disclaimer
```

## Tools (MCP)
1. `analyze_patterns(time_range: str = "last_60_days")` -> {patterns, correlations, anomalies, confidence, sources}
2. `simulate_whatif(scenario: dict)` -> {projected_outcomes, based_on, confidence}
3. `generate_report(format: "markdown"|"json"|"html", include_timeline: bool)` -> report

## Collaboration Protocol (Simple)
- Host calls sidecar tool (e.g. `collaborative_insight`).
- Sidecar may return `needs_context: { "calendar": true }` when life-event context is missing.
- Host re-calls with `host_context.events[]` where each event has `date`, `type` (`travel` | `deadline`), optional `note`.
- See `code/health-mcp-starter/docs/COLLABORATION.md` for full request/response shapes and mcporter examples.

## Privacy & Security
- Scoped paths only.
- All accesses logged to audit.log
- No outbound network by default.
- Auto-disable after TTL.

## Quality Gates (inspired by agent-skills)
- Every analysis must cite exact excerpts.
- Confidence score 0-1.
- Disclaimer always.
- Use stats where possible (pandas).

This spec to be implemented in Phase 3 of the plan.