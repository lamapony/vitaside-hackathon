# VitaCo / VitaSide — Short Hackathon Description (Realistic Version)

**VitaSide is personal pattern intelligence for self-observation and preparation for medical visits.**

It runs as a local sidecar inside your personal AI agent (via MCP). It analyzes your own data — Omi voice notes, Apple Health exports, and journals — to surface real patterns, correlations (including time lags), anomalies against your personal baseline, and "what-if" simulations of lifestyle changes.

It produces structured reports with timelines, cited examples, confidence scores, and clear observations.

### Who it's for
- People who already do detailed self-tracking (Omi + wearables + notes) and want to understand themselves better.
- Data-savvy doctors who work with patients who bring digital data.

### Core positioning (what it actually is)
- **Not** a medical diagnostic tool.
- Omi data is noisy and subjective — it does not produce precise medical conclusions.
- Primary value: better self-observation and arriving at the doctor's office with specific, data-backed questions and timelines instead of vague feelings like "I don't feel well."

### How it works
- Add a local MCP server to your Hermes (or compatible agent).
- Analysis runs entirely on your machine.
- Generate and optionally share a clean report with your doctor.

**Tech stack:** MCP (FastMCP), Hermes Agent, Omi + Apple Health, lightweight analytics (pandas/scipy).

This is a tool for people who already invest time in tracking their life and want to get more meaningful insight from it. It is not a revolution in medicine — it is practical personal pattern intelligence for self-awareness and better doctor visits.

---

## English Positioning Statement (for pitch, website, README)

**VitaSide is personal pattern intelligence for self-observation and preparation for medical visits.**

It lives as a temporary, local sidecar inside your main personal AI agent. Using the data you already collect — voice reflections (Omi), wearable metrics (Apple Health), and notes — it helps you see clear patterns in how you live and how you feel.

Instead of guessing or forgetting important details between appointments, you get:
- Longitudinal timelines of your signals
- Correlations with time lags (e.g., "high activity days followed by poor sleep often lead to low mood the next day")
- Anomalies relative to your own baseline
- Simple "what-if" simulations based on your historical data

The output is designed to help you understand your own patterns better and prepare more effectively for visits with your doctor — with specific observations, cited examples from your data, and confidence levels.

**Key principles:**
- Strictly personal use and self-observation first
- Not a diagnostic or treatment tool
- Everything runs locally with full user control
- Temporary and scoped access when shared with a doctor
- Transparent: every insight includes sources and limitations

This is quantified-self intelligence that actually helps you show up to medical appointments with clarity instead of confusion.