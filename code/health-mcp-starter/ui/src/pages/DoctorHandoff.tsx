import { useEffect, useState } from "react";
import { ClinicalSummary, Questions, UserContext, postJson, getJson } from "../api";
import { Activity, FileText, Share2, Download, UserCheck } from "lucide-react";

type ExportResult = {
  outputs?: Record<string, string>;
  latest?: { patient_html?: string; doctor_html?: string; user_context?: string };
  questions_count?: number;
  anonymized?: boolean;
  payload_fingerprint?: string;
  share_url?: string | null;
  upload_token_preview?: string;
  note?: string;
};

type AzureContract = {
  azure_enabled?: boolean;
  mode?: string;
  allowed_operations?: string[];
};

type Props = {
  questions?: Questions;
  context?: UserContext;
};

export function DoctorHandoff({ questions, context }: Props) {
  const [anonymize, setAnonymize] = useState(false);
  const [exportResult, setExportResult] = useState<ExportResult | null>(null);
  const [azureContract, setAzureContract] = useState<AzureContract | null>(null);
  const [azureResult, setAzureResult] = useState<ExportResult | null>(null);
  const [skinResult, setSkinResult] = useState<any>(null);
  const [clinicalSummary, setClinicalSummary] = useState<ClinicalSummary | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getJson<ClinicalSummary>("/api/clinical-summary")
      .then(setClinicalSummary)
      .catch(() => setClinicalSummary(null));
  }, []);

  async function generateBundle() {
    setBusy(true);
    try {
      setExportResult(await postJson<ExportResult>("/api/export-bundle", { anonymize }));
    } finally {
      setBusy(false);
    }
  }

  async function previewAzure() {
    setAzureContract(await getJson<AzureContract>("/api/azure-contract"));
  }

  async function shareAzure() {
    const confirmed = window.confirm(
      "Send a minimized, anonymized summary for optional enrichment or sharing? Raw notes stay local."
    );
    if (!confirmed) return;
    setAzureResult(await postJson<ExportResult>("/api/azure/enhance", {
      user_consent: true,
      anonymize: true,
      prompt_hint: "Clinical handoff summary",
      locale: "ru"
    }));
  }

  return (
    <section>
      <header className="page-header">
        <div>
          <p className="eyebrow">Clinical preparation</p>
          <h1>Doctor handoff package</h1>
          <p className="lede">
            Structured observations, cited excerpts, and focused questions. All processing happens locally. Export for your appointment.
          </p>
        </div>
      </header>

      {clinicalSummary && (clinicalSummary.headline || clinicalSummary.trends?.length) ? (
        <div className="card clinical-summary-card">
          <div className="card-header">
            <div className="card-title">Clinical summary</div>
            <Activity size={18} />
          </div>
          {clinicalSummary.headline && (
            <div className="clinical-headline">{clinicalSummary.headline}</div>
          )}
          {clinicalSummary.trends && clinicalSummary.trends.length > 0 && (
            <div className="clinical-trends">
              <p className="eyebrow" style={{ marginBottom: 12 }}>Trends</p>
              <div className="trend-list">
                {clinicalSummary.trends.map((trend, index) => (
                  <div className="trend-row" key={`${trend.signal ?? trend.label}-${index}`}>
                    <div className="trend-label">
                      <strong>{trend.label ?? trend.signal?.replace(/_/g, " ") ?? "Signal"}</strong>
                      {trend.period && <span className="meta">{trend.period}</span>}
                    </div>
                    <div className="trend-values">
                      {trend.delta_14d != null && (
                        <span className={`trend-delta ${trend.delta_14d >= 0 ? "up" : "down"}`}>
                          14d {trend.delta_14d >= 0 ? "+" : ""}{Math.round(trend.delta_14d * 100)}%
                        </span>
                      )}
                      {trend.delta_90d != null && (
                        <span className={`trend-delta ${trend.delta_90d >= 0 ? "up" : "down"}`}>
                          90d {trend.delta_90d >= 0 ? "+" : ""}{Math.round(trend.delta_90d * 100)}%
                        </span>
                      )}
                      {trend.direction && trend.delta_14d == null && trend.delta_90d == null && (
                        <span className={`trend-delta ${trend.direction}`}>{trend.direction}</span>
                      )}
                    </div>
                    {trend.detail && <div className="meta">{trend.detail}</div>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : null}

      <div className="card">
        <div className="card-header">
          <div className="card-title">Questions to discuss</div>
          <UserCheck size={18} />
        </div>
        {questions?.questions?.length ? (
          <ul style={{ paddingLeft: 20, margin: 0 }}>
            {questions.questions.slice(0, 7).map((q, i) => (
              <li key={i} style={{ marginBottom: 10, lineHeight: 1.5 }}>
                {q.question}
                {q.evidence && <div style={{ fontSize: 13, color: 'var(--ink-3)', marginTop: 2 }}>— {q.evidence}</div>}
              </li>
            ))}
          </ul>
        ) : (
          <div className="meta">No questions yet. Add context or daily notes for better preparation.</div>
        )}
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-header">
            <div className="card-title">Export for your visit</div>
            <Download size={18} />
          </div>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14, fontSize: 14 }}>
            <input 
              type="checkbox" 
              checked={anonymize} 
              onChange={e => setAnonymize(e.target.checked)} 
            />
            Anonymize personal excerpts
          </label>
          <button className="primary" onClick={generateBundle} disabled={busy}>
            {busy ? "Preparing documents..." : "Generate patient summary + doctor report"}
          </button>

          {exportResult && (
            <div style={{ marginTop: 16, fontSize: 13 }}>
              <div style={{ color: 'var(--success)', marginBottom: 6 }}>Documents ready in <code>out/</code></div>
              {exportResult.outputs && Object.entries(exportResult.outputs).map(([k, v]) => (
                <div key={k} style={{ margin: '3px 0' }}>• {k}: <code>{v}</code></div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-title">Optional enrichment (Azure)</div>
            <Share2 size={18} />
          </div>
          <p style={{ color: 'var(--ink-2)', fontSize: 14, lineHeight: 1.5 }}>
            Send a heavily minimized payload (no raw notes) for richer narrative or a shareable link. Only with your explicit consent.
          </p>

          <div style={{ display: 'flex', gap: 8, marginTop: 14 }}>
            <button className="secondary" onClick={previewAzure}>Preview what is sent</button>
            <button className="primary" onClick={shareAzure} disabled={busy}>Share minimized summary</button>
          </div>

          {azureContract && (
            <div className="meta" style={{ marginTop: 12 }}>
              Mode: {azureContract.mode || 'stub'} • Enabled: {String(azureContract.azure_enabled)}
            </div>
          )}
          {azureResult && azureResult.share_url && (
            <div style={{ marginTop: 10 }}>
              <a href={azureResult.share_url} target="_blank" rel="noreferrer" style={{ fontWeight: 500 }}>
                Open shared clinical summary →
              </a>
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">Preliminary skin photo check (optional)</div>
        </div>
        <p style={{ color: 'var(--ink-2)', fontSize: 14 }}>
          Upload photo of mole/spot. Local ABCDE features + disclaimer. External only with consent. <strong>NOT diagnosis.</strong> See doctor.
        </p>
        <div style={{ marginTop: 12 }}>
          <input 
            type="file" 
            accept="image/*" 
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                const formData = new FormData();
                formData.append("file", file);
                formData.append("user_consent", "true");
                formData.append("use_external", "false");
                fetch("/api/analyze-skin-photo", { method: "POST", body: formData })
                  .then(r => r.json())
                  .then(setSkinResult)
                  .catch(console.error);
              }
            }}
          />
          {skinResult && (
            <div style={{ marginTop: 16, fontSize: 13 }}>
              <div><strong>Local analysis</strong> — risk score ~{Math.round((skinResult.risk_score || 0)*100)}%</div>
              <div>Flags: {(skinResult.preliminary_flags || []).join(", ") || "none"}</div>
              <div className="meta" style={{ marginTop: 6 }}>{skinResult.recommendation}</div>
              {skinResult.external && <div className="meta">External stub: {skinResult.external.note}</div>}
            </div>
          )}
        </div>
      </div>

      <div className="disclaimer">
        VitaSide extracts patterns from your personal data only. This is not medical advice or a diagnosis. 
        Always discuss observations with a qualified clinician.
      </div>
    </section>
  );
}
