# VitaSide — The Sidecar Protocol for Agentic Personal Health Intelligence

**Hackathon Pitch (Voluminous, Powerful, "Wow" Version with Real Winning Chance)**

**One-Line Hook:**
VitaSide is personal pattern intelligence for self-observation and preparation for medical visits. It runs as a temporary local sidecar inside your personal AI agent, turning your own Omi voice notes, Apple Health data, and journals into clear patterns, time-lagged correlations, anomalies, and "what-if" simulations — so you understand yourself better and arrive at doctor appointments with specific, data-backed observations instead of vague feelings.

## The Problem (Emotional + Universal Pain)

Doctors see patients in 10-15 minute snapshots. Patients live 24/7 with fragmented, noisy data:
- Omi voice memos ("I slept like shit again after that late coffee")
- Apple Health numbers (sleep stages, HRV, steps, SpO2)
- Obsidian notes, calendars, wearables

No one connects them longitudinally. Result:
- Doctors prescribe based on self-reported "I feel tired" instead of "Your REM drops 38% on high-stress + low-sleep days, and this has happened 14 times in 9 weeks."
- Patients gaslight themselves or miss obvious lifestyle triggers.
- The information asymmetry between "how I actually live" and "what my doctor knows" is massive.

Existing solutions are broken:
- Cloud health apps = privacy nightmare.
- Generic AI coaches = shallow and one-size-fits-all.
- Wearable dashboards = numbers without life context.
- Paper or basic exports = useless for pattern detection.

This is not a small problem. It's why lifestyle medicine often fails — the data loop is broken.

## The Big Idea: VitaSide — Doctor-Issued Living Sidecars via MCP

**Core Innovation:** An open protocol (built on MCP) for **temporary, scoped expert AI sidecars** that a doctor (or specialist) can "issue" to a patient's main personal agent (Hermes or any MCP-compatible agent).

The sidecar:
- Lives *inside* the patient's agent (no new app, no cloud sync required).
- Brings domain-specific intelligence (e.g. "sleep-metabolism-stress mapper", "post-viral recovery pattern detector", "ADHD lifestyle trigger finder").
- Gets time-limited, audited, read-only access only to approved data sources (Omi conversations, Apple Health export, specific Obsidian folders).
- **Collaborates** with the main agent: they delegate, debate, combine knowledge ("Main agent knows you had 3 late flights last month; sidecar knows the biometric impact").
- Produces not raw data, but **patterns + explanations + what-if simulations**.
- Auto-expires or can be revoked instantly. Full audit trail.

**Why this is "wow" and different:**
- It's not another health app. It's a new primitive for **safe expert intelligence injection** into personal AI.
- Privacy-first by architecture: doctor never sees raw data unless patient explicitly exports a report.
- Temporary by design — perfect for observation periods, new treatments, or targeted monitoring.
- Voice becomes first-class: Omi turns casual spoken life into structured signals.
- Multi-agent superpowers: Generalist (your main Hermes that knows your full context) + Specialist (sidecar) = insights neither could produce alone.
- Extensible protocol: Any doctor/specialist can create and distribute their own sidecar. One patient can run multiple in parallel.

## Hackathon Demo (What We Ship in 48 Hours + Make Judges Stand Up)

**Narrative Flow (5-7 minute killer demo):**

1. **Issuing the Sidecar (30 sec)**
   - "Doctor" (us) generates a simple VitaSide manifest (YAML) for "Sleep-Stress-Metabolism Specialist".
   - Patient (you) adds one line to Hermes config or runs a one-command install.
   - Sidecar appears as native tools in your agent: `mcp_vitaside_analyze`, `mcp_vitaside_simulate`, etc.

2. **Live Pattern Discovery in Chat**
   - User: "Why do I feel brain fog after workouts lately?"
   - Main Hermes agent: "Let me check your recent notes and calendar..."
   - VitaSide sidecar activates: pulls real Omi + Apple data with advanced parsing (context words like "сегодня/вчера", speaker separation, time-of-day, lag correlations 1-3 days, anomalies vs *your personal baseline*).
   - They collaborate in the background.
   - Result: "On days with >8000 steps + <6.5h sleep, your Omi notes mention 'brain fog' or low energy 4x more often in the following 48h. This pattern appears in 11 of last 22 high-activity days. HRV also dips."

3. **The "Wow" What-If Simulation**
   - User: "What if I fixed my sleep to consistent 7.5 hours for the next two weeks?"
   - Sidecar runs simulation based on *your historical patterns* (simple statistical model + pattern matching).
   - Output: "Based on your data, expect ~28% fewer low-mood signals, better average HRV, and reduced mentions of afternoon fatigue. Confidence: medium (your data has 3 similar periods)."

4. **Beautiful, Doctor-Ready Output**
   - Interactive timeline (HTML with bars for sleep, activity, mood signals, annotated events from Omi).
   - Top patterns ranked by strength + real example quotes + dates.
   - Full structured export (JSON + Markdown report + visual).
   - Audit log: "Sidecar accessed 47 Omi files + 30 days Apple Health. No data left the device."

5. **Doctor Side (Closing the Loop)**
   - Patient exports the report (one command).
   - Simulated "doctor view": clean timeline + highlighted patterns. Doctor can see exactly what the sidecar found without raw data dump.

**Technical Depth We Can Actually Show:**
- Real data from your vault (hundreds of Omi files).
- Advanced Omi parser (timestamps, context, speakers, quality scoring) — already prototyped.
- Apple Health XML parsing + metrics.
- Temporal correlations, anomalies, baseline stats (pandas/scipy).
- MCP native integration + tool calling.
- Multi-agent collaboration (main Hermes + sidecar).
- Local-only, fast, auditable.
- Bonus: simple web timeline visualizer (static HTML/JS that we generate).

This is not vaporware. The core analysis engine exists. We polish, extend with simulation + collaboration + beautiful output + protocol wrapper.

## Why This Has a Serious Chance to Win

**Novelty (Judges love new primitives):**
- First real demo of MCP for "expert sidecar injection" into personal agents.
- Agent-to-agent collaboration in a high-stakes, privacy-sensitive domain.
- Protocol that makes specialist AI portable and temporary.

**Impact + Emotional Resonance:**
- Solves a problem every human who has seen a doctor has felt.
- Privacy-respecting health AI in 2026 is rare and valuable.
- Real social good without overclaiming medical diagnosis (we are explicit: "patterns for awareness and better doctor conversations").

**Demo Quality:**
- Live on *your actual data* = authenticity that beats fake dashboards.
- End-to-end story: issue → analyze → simulate → export.
- Visuals + numbers + natural language = satisfying.

**Technical Credibility:**
- Leverages real existing stack (Hermes + MCP + Omi pipeline + Apple Health + Obsidian).
- We already have working code for parsing, correlations, reports.
- Shows deep understanding of multi-agent systems.

**Future Vision (Scalable Story):**
- Open protocol — any specialist creates sidecars.
- One patient can run sleep sidecar + metabolic sidecar + mental health sidecar simultaneously.
- Extends beyond health (productivity sidecars, relationship sidecars...).
- Positions Hermes ecosystem as the platform for safe, temporary expert augmentation.

**Risk Mitigation (We Address Criticisms Head-On):**
- No medical device claims: "Personal pattern intelligence for self-observation and preparation for medical visits."
- Local-first + temporary + audited by design.
- Data quality issues acknowledged (we show confidence scores and example quotes).
- Adoption path: starts with quantified-self users + data-friendly doctors (exact audience already in Hermes/Omi).

## Architecture (Hackathon Scope + Extensible)

- **Protocol**: Simple Sidecar Manifest (name, allowed data scopes, tools, TTL, optional "doctor signature").
- **Sidecar Server** (Python/FastMCP — extend current `health-pattern-mcp.py`):
  - Parsers (Omi advanced + Apple Health).
  - Analysis engine (lags, anomalies, baseline, simple simulation).
  - Collaboration interface (can query main agent for context).
  - Report generators (rich Markdown + HTML timeline + JSON).
- **Host (Hermes)**: Loads sidecar as MCP tools. Main agent decides when to invoke or delegate.
- **Issuing**: One-file manifest + server script. Patient adds to config.
- **Audit & Control**: Everything logged. Patient can inspect/disable anytime.

**Existing Foundation We Build On:**
- health-pattern-mcp.py (Omi parser, Apple support, analyze, correlate, reports).
- Real Omi vault data.
- Hermes MCP integration knowledge.
- Critique and realistic positioning already done.

## Scope for 48h Hackathon

**Must Ship:**
- Protocol spec (short Markdown).
- Polished VitaSide MCP server with simulation + collaboration hooks.
- End-to-end demo flow (issue → chat interaction → what-if → export).
- Beautiful timeline visual (HTML/JS).
- Pitch deck + live story.

**Nice to Have (if time):**
- Multiple sidecar types.
- Simple web "doctor view".
- Voice demo (Omi live snippet).

This is ambitious but grounded — we have the core engine.

## Final Pitch Paragraph (for judges / README)

"VitaSide is personal pattern intelligence for self-observation and preparation for medical visits. It lives as a temporary local sidecar inside your personal AI agent. Using the data you already collect — Omi voice notes, Apple Health, and journals — it surfaces patterns, time-lagged correlations, anomalies vs your baseline, and what-if simulations. The goal is to help you understand your own life better and show up to medical appointments with clear, data-backed observations instead of vague feelings. Everything runs locally with full user control. We built a working reference implementation and demo on real personal data."

This is voluminous, technically deep, emotionally powerful, privacy-respecting, and actually buildable on top of what we already have.

Let's win.