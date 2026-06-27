# VitaSide Hackathon Demo Script

## Setup (5 min before demo)
- Have Hermes running or simulated.
- Pre-load the sidecar manifest.
- Have real data ready (anonymized if needed).
- Run the full flow script in background if needed.

## Live Demo Flow (6-8 minutes)

1. **Introduction (30s)**
   - "VitaSide: Doctor issues a temporary AI sidecar that lives inside your personal agent."
   - Show the problem: doctor blind spot.

2. **Issuing the Sidecar (1 min)**
   - Run: `./issue-sidecar.sh sleep-stress-sidecar`
   - Show manifest.
   - "Patient adds to config: one line."

3. **Live Analysis (2 min)**
   - In chat: "Analyze my patterns for sleep and mood last 60 days."
   - Show sidecar activating.
   - Output: patterns with citations from Omi, correlations with lags, anomalies.
   - "See? It found 'after late coffees + high steps, mood tanks next day' with examples."

4. **What-If Wow (1.5 min)**
   - "What if I slept 7.5h consistently?"
   - Run simulate.
   - Show projected improvements based on your real past data.

5. **Report & Export (1 min)**
   - Generate HTML timeline report.
   - Show visual (bars, annotations).
   - "Export for doctor" - structured + narrative.

6. **Collaboration Demo (1 min)**
   - "Main agent knows my travel from notes. Sidecar knows biometrics."
   - Show combined insight.

7. **Close & Why (30s)**
   - Privacy: local, temporary, audited.
   - Protocol extensible.
   - "This is how personal agents get specialized intelligence safely."

**Backup:** Pre-recorded video of full flow if live fails. Have screenshots.

**Props:** Terminal, browser for HTML report, perhaps simple web mock for "doctor view".

Run the full end-to-end before judges.