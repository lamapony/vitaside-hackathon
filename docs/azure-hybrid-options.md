# Azure Services for VitaSide — Hybrid Options to Make the Project More Useful

> **Implementation contract (for Azure agent):** see [`AZURE-CONTRACT.md`](./AZURE-CONTRACT.md) and modules `azure_contract.py` / `azure_boost.py`.

**Context**: VitaSide is deliberately **local-first, privacy-first, temporary sidecar**. Raw health data (Omi transcripts, Apple Health) never leaves the user's machine by default.

**Goal of Azure integration**: Make the project *more useful* without breaking core principles. Use Azure for:
- Stronger AI reasoning
- Better doctor-side tools and interoperability
- Scalability for pilots
- Hackathon "wow" (enterprise-grade components)
- Free credits / easy hosting

**Core Rule**: All raw personal data stays local. Azure receives only:
- Aggregated features / statistics
- Embeddings (if opted-in)
- Explicitly exported reports (patient consent + expiration)
- Never full transcripts or full health exports

## Recommended Azure Services (Prioritized for Usefulness)

### 1. Azure OpenAI Service (Highest Impact for "Useful")
**Why it makes the project better**:
- Current local analysis uses simple pandas/scipy + templates.
- Azure OpenAI can turn raw patterns into rich, natural-language insights, explanations, and personalized advice.
- Better "what-if" simulations with reasoning chains.
- Generate doctor-friendly narratives from structured data.
- Handle noisy Omi language better (summarization, entity extraction).

**How to integrate (hybrid)**:
- Add optional tool in the MCP server: `azure_enhance_insight(patterns_json, user_consent=True)`
- Locally compute patterns → send **only** anonymized aggregates + embeddings (via Azure AI Embeddings) + prompt.
- Use Azure OpenAI with:
  - Private Endpoints / VNet
  - Data residency (EU or chosen region)
  - Content filters + Responsible AI
  - Managed Identity (no keys in code)
- Response comes back as enriched text / structured JSON.

**Hackathon value**: Show "local core + cloud intelligence boost" toggle. Judges love hybrid AI.

**Cost**: Free tier + credits usually available for hackathons.

### 2. Azure Health Data Services (FHIR)
**Why useful**:
- Doctors and clinics use FHIR for interoperability.
- Turn VitaSide reports into proper FHIR Observation / Condition / DocumentReference resources.
- Makes the "export to doctor" actually usable in real EHR systems.

**Integration**:
- Local sidecar generates JSON report.
- Optional Azure Function that converts to FHIR (patient uploads consented, minimal data).
- Use Azure Health Data Services workspace + FHIR server.

**Value**: Turns the project from "personal tool" into something that can actually flow into medical workflows.

### 3. Azure Machine Learning (for Advanced Analytics)
**Why**:
- Current correlations/anomalies are basic.
- Host better time-series models (Prophet, LSTM, or AutoML) for:
  - More accurate what-if forecasting
  - Personalized baseline modeling
  - Anomaly detection with uncertainty
- Train on user's historical data (or synthetic + fine-tune).

**Hybrid pattern**:
- Local: feature extraction
- Azure ML endpoint: model inference on features only
- Use Azure ML Managed Online Endpoint with private link.

**Alternative (simpler for hackathon)**: Use Azure AutoML to generate a model, then export as ONNX and run locally (keeps data local).

### 4. Azure Static Web Apps + Azure Functions (Doctor / Demo Side)
**Why**:
- Host beautiful, shareable report viewer.
- Doctor portal where patient can send time-limited, encrypted report link.
- Serverless backend for report processing, PDF generation, email (with consent).

**Implementation**:
- Static Web App hosts the HTML timeline visualizer (already in our code).
- Azure Function: `/upload-report` (receives encrypted JSON, stores temporarily in Blob with SAS + expiration, generates nicer view).
- Use Azure AD (Entra ID) for doctor authentication if needed.

**Hackathon demo**:
- Local analysis → "Share with doctor" button → generates link hosted on Azure → doctor sees clean dashboard.

### 5. Azure AI Search + Embeddings
- Semantic search over user's Omi notes + reports.
- When asking "why do I feel bad after workouts?", the sidecar can retrieve relevant past notes via Azure AI Search (send only embeddings, not full text if paranoid).
- Useful for RAG-style pattern explanation.

### 6. Other Supporting Services
- **Azure Key Vault**: Secure storage of any API keys / connection strings for the optional cloud parts.
- **Azure Blob Storage** (encrypted at rest, customer-managed keys): Temporary storage of consented exports.
- **Azure Monitor + Application Insights**: Telemetry for the sidecar itself (performance, errors) — opt-in, no health data.
- **Entra ID (Azure AD)**: Secure sidecar issuance protocol (doctor "signs" a manifest using app registration).
- **Azure Translator**: If we want multi-language support for non-Russian users.
- **Power BI Embedded**: Advanced interactive dashboards for reports (can embed in the HTML output).

## Proposed Architecture (Hybrid, Privacy-Preserving)

```
User's Machine (Hermes + VitaSide MCP)
├── Local parsing (Omi + Apple)
├── Local basic stats (pandas/scipy)
├── Optional: send features/embeddings → Azure OpenAI / Azure ML
│   (user toggle + consent)
└── Generate report locally
    └── Optional: upload consented report → Azure Static Web Apps / Functions (FHIR + nice UI)
           ↓
Doctor sees (time-limited, encrypted, no raw data)
```

**Consent & Control**:
- All Azure features behind explicit `enable_azure_boost: false` in manifest.
- Audit log records every cloud call.
- Data minimization: only what's necessary.

## Hackathon Strategy

**Minimal viable Azure addition** (easy to demo):
1. Azure Static Web Apps for the report visualizer.
2. One Azure Function for "share report" flow.
3. Azure OpenAI (or fallback to local) for natural language "explain this pattern" tool.

This adds polish and "real product" feel without complexity.

**Bigger vision** (for after hackathon):
- Full hybrid with Azure OpenAI + FHIR.
- Makes VitaSide useful for actual doctors (interoperability).
- Positions it as "local intelligence + enterprise cloud when needed".

## Risks & Mitigations

- **Privacy risk**: Mitigate with strict opt-in, data minimization, documentation of exactly what leaves the device.
- **Complexity**: Keep core 100% functional without Azure. Azure is "boost".
- **Cost / Lock-in**: Use only pay-as-you-go + free tiers. Document alternatives (local LLMs via Ollama, etc.).
- **Regulatory**: Emphasize we are not processing PHI in cloud without consent; patterns only.

## Next Steps (for this hackathon project)

1. Add `azure_boost` optional tools to the MCP server (using Azure SDK).
2. Create a simple Azure Function + Static Web App for report sharing.
3. Update the demo script to show the toggle.
4. Add section to the pitch: "Hybrid local + Azure for real-world usefulness".
5. Document exact data flows in the SPEC.

This keeps the soul of the project (local, private, user-controlled) while making it significantly more powerful and credible for real use and for judges.

---

**Files to extend**:
- `code/health-mcp-starter/health-pattern-mcp.py` (add optional Azure calls)
- `plan/TASKS.md` (add Azure tasks)
- `VitaSide-Hackathon-Pitch.md` (add hybrid story)

This approach was chosen because it directly addresses "make the project more useful" while respecting the local-first DNA established in the critique and reframing.