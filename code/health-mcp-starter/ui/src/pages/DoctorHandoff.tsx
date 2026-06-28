import { useEffect, useState } from "react";
import { ClinicalSummary, Questions, UserContext, postJson, getJson } from "../api";
import { Activity, FileText, Share2, Download, UserCheck, Printer } from "lucide-react";
import { PrintPacket } from "../components/PrintPacket";

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

type AzurePreview = {
  operation?: string;
  payload?: { summary?: string; confidence?: number; signals?: string[] };
  data_minimization?: { payload_fingerprint?: string; forbidden_categories?: string[] };
  note?: string;
};

type Props = {
  questions?: Questions;
  context?: UserContext;
};

export function DoctorHandoff({ questions, context }: Props) {
  const [anonymize, setAnonymize] = useState(false);
  const [exportResult, setExportResult] = useState<ExportResult | null>(null);
  const [azureContract, setAzureContract] = useState<AzureContract | null>(null);
  const [azurePreview, setAzurePreview] = useState<AzurePreview | null>(null);
  const [azureResult, setAzureResult] = useState<ExportResult | null>(null);
  const [skinResult, setSkinResult] = useState<any>(null);
  const [skinError, setSkinError] = useState<string | null>(null);
  const [skinBusy, setSkinBusy] = useState(false);
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
    const [contract, preview] = await Promise.all([
      getJson<AzureContract>("/api/azure-contract").catch(() => null),
      getJson<AzurePreview>("/api/preview-azure").catch(() => null),
    ]);
    setAzureContract(contract);
    setAzurePreview(preview);
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
      locale: "en"
    }));
  }

  return (
    <>
    <section className="screen-only">
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
          <button className="secondary" onClick={() => window.print()} style={{ marginTop: 10 }}>
            <Printer size={16} /> Print / Save as PDF
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
          {azurePreview && (
            <div className="meta" style={{ marginTop: 10, lineHeight: 1.6 }}>
              {azurePreview.data_minimization?.payload_fingerprint && (
                <div>Payload fingerprint: <code>{azurePreview.data_minimization.payload_fingerprint}</code></div>
              )}
              {azurePreview.data_minimization?.forbidden_categories?.length ? (
                <div>Forbidden: {azurePreview.data_minimization.forbidden_categories.join(", ")}</div>
              ) : null}
              {azurePreview.payload?.summary && (
                <div>Payload: {azurePreview.payload.summary}</div>
              )}
              {azurePreview.note && <div style={{ color: 'var(--ink-3)', marginTop: 4 }}>{azurePreview.note}</div>}
            </div>
          )}
          {azureResult && azureResult.share_url && (
            <div style={{ marginTop: 10 }}>
              <a href={azureResult.share_url} target="_blank" rel="noreferrer" style={{ fontWeight: 500 }}>
                Open shared clinical summary →
              </a>
            </div>
          )}
          {azureResult && !azureResult.share_url && azureResult.note && (
            <div className="meta" style={{ marginTop: 10 }}>{azureResult.note}</div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">Skin photo ABCDE check (optional)</div>
        </div>
        <p style={{ color: 'var(--ink-2)', fontSize: 14, lineHeight: 1.5 }}>
          Upload a photo and get <strong>descriptive ABCDE-inspired features</strong> only —
          not a diagnosis, not a risk score. For any skin concern, see a dermatologist.
        </p>

        <details style={{ marginTop: 8, fontSize: 13 }}>
          <summary style={{ cursor: 'pointer', color: 'var(--ink-3)' }}>How to photograph a skin spot</summary>
          <ul style={{ marginTop: 8, paddingLeft: 20, color: 'var(--ink-2)' }}>
            {(skinResult?.photo_guide ?? [
              'Use bright, diffuse, natural lighting (avoid harsh shadows and flash).',
              'Photograph the spot straight-on, filling most of the frame.',
              'Place a ruler or coin next to the spot for size reference.',
              'Keep the camera steady and in focus.',
            ]).map((g: string, i: number) => (
              <li key={i} style={{ marginBottom: 4 }}>{g}</li>
            ))}
          </ul>
        </details>

        <div style={{ marginTop: 12 }}>
          <input
            type="file"
            accept="image/*"
            disabled={skinBusy}
            onChange={async (e) => {
              const file = e.target.files?.[0];
              if (!file) return;
              const MAX = 15 * 1024 * 1024;
              if (file.size > MAX) {
                setSkinResult({
                  error: `file too large (max ${Math.round(MAX / (1024 * 1024))} MB)`,
                  disclaimer: 'Use a smaller or compressed image.',
                });
                return;
              }
              const confirmed = window.confirm(
                'Analyse this photo locally on this device? The image stays on your machine unless you enable external analysis. This is NOT a diagnosis.'
              );
              if (!confirmed) return;
              setSkinBusy(true);
              setSkinResult(null);
              try {
                const formData = new FormData();
                formData.append("file", file);
                formData.append("user_consent", "true");
                formData.append("use_external", "false");
                const r = await fetch("/api/analyze-skin-photo", { method: "POST", body: formData });
                const data = await r.json();
                setSkinResult(data);
                if (!r.ok || data.error) {
                  setSkinError(data.error || `request failed (${r.status})`);
                } else {
                  setSkinError(null);
                }
              } catch (err) {
                setSkinError(String(err));
                setSkinResult(null);
              } finally {
                setSkinBusy(false);
              }
            }}
          />
          {skinBusy && <div className="meta" style={{ marginTop: 8 }}>Analysing image locally…</div>}
          {skinError && (
            <div style={{ marginTop: 10, fontSize: 13, color: 'var(--danger, #b91c1c)' }}>
              Could not analyse: {skinError}
            </div>
          )}
          {skinResult && !skinResult.error && (
            <div style={{ marginTop: 16, fontSize: 13 }}>
              <div><strong>Local ABCDE description</strong></div>
              <ul style={{ marginTop: 6, paddingLeft: 20 }}>
                {(skinResult.observations ?? []).map((obs: string, i: number) => (
                  <li key={i} style={{ marginBottom: 4 }}>{obs}</li>
                ))}
              </ul>
              {skinResult.abcde_observations && (
                <div className="meta" style={{ marginTop: 6 }}>
                  diameter {skinResult.abcde_observations.diameter_px}px ·
                  asymmetry {skinResult.abcde_observations.asymmetry} ·
                  border {skinResult.abcde_observations.border_contrast} ·
                  colours {skinResult.abcde_observations.distinct_colors}
                </div>
              )}
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
    <PrintPacket
      className="print-only"
      visitDate={new Date().toISOString().slice(0, 10)}
      profile={context?.profile}
      clinicalSummary={clinicalSummary}
      questions={questions}
    />
    </>
  );
}
