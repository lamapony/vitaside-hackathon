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

type AzureDataMin = {
  payload_fingerprint?: string;
  raw_transcripts?: boolean;
  vault_paths?: boolean;
  anonymized?: boolean;
  max_excerpt_chars?: number;
  forbidden_categories?: string[];
};

type AzurePreview = {
  operation?: string;
  note?: string;
  payload?: {
    contract_version?: string;
    summary?: string;
    local_summary?: { days_analyzed?: number; files_scanned?: number };
    data_minimization?: AzureDataMin;
    consent?: { operation?: string };
  };
  data_minimization?: AzureDataMin;
};

type Props = {
  questions?: Questions;
  context?: UserContext;
};

function humanizeSignal(s: string): string {
  const known: Record<string, string> = {
    stress: "Stress",
    mood_low: "Low mood",
    mood_good: "Good mood",
    sleep: "Sleep",
    sleep_quality: "Sleep quality",
    symptom_pain: "Pain / symptom",
    headache: "Headache",
  };
  return known[s] ?? s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

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
                {clinicalSummary.trends.map((trend, index) => {
                  const delta14 = trend.delta ?? trend.delta_14d;
                  const recent = trend.recent_14d ?? trend.recent_freq;
                  const prior = trend.prior_14d ?? trend.prior_freq;
                  const label = trend.label ?? trend.signal ?? "Signal";
                  const arrow = trend.direction === "up" ? "↑" : trend.direction === "down" ? "↓" : trend.direction === "stable" ? "→" : "";
                  return (
                    <div className="trend-row" key={`${label}-${index}`}>
                      <div className="trend-label">
                        <strong>{humanizeSignal(label)}</strong>
                        <span className="meta">14d vs prior</span>
                      </div>
                      <div className="trend-values">
                        {delta14 != null && (
                          <span className="trend-delta">{arrow} {delta14 >= 0 ? "+" : ""}{Math.round(delta14 * 100)}%</span>
                        )}
                        {recent != null && prior != null && (
                          <span className="meta">{Math.round(recent * 100)}% recent · {Math.round(prior * 100)}% prior</span>
                        )}
                      </div>
                      {trend.detail && <div className="meta">{trend.detail}</div>}
                    </div>
                  );
                })}
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
          <ol className="question-list">
            {questions.questions.slice(0, 7).map((q, i) => (
              <li key={i}>
                <div>{q.question}</div>
                {q.evidence && <div className="question-evidence">{q.evidence}</div>}
              </li>
            ))}
          </ol>
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
          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={anonymize}
              onChange={e => setAnonymize(e.target.checked)}
            />
            Anonymize personal excerpts
          </label>
          <div className="button-stack">
            <button className="primary" onClick={generateBundle} disabled={busy}>
              {busy ? "Preparing documents..." : "Generate patient summary + doctor report"}
            </button>
            <button className="secondary" onClick={() => window.print()}>
              <Printer size={16} /> Print / Save as PDF
            </button>
          </div>

          {exportResult && (
            <div className="export-result">
              <div className="ok">Documents ready in <code>out/</code></div>
              {exportResult.outputs && Object.entries(exportResult.outputs).map(([k, v]) => (
                <div key={k} className="line">• {k}: <code>{v}</code></div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-title">Optional enrichment (Azure)</div>
            <Share2 size={18} />
          </div>
          <p className="card-lede">
            Send a heavily minimized payload (no raw notes) for richer narrative or a shareable link. Only with your explicit consent.
          </p>

          <div className="button-row">
            <button className="secondary" onClick={previewAzure}>Preview what is sent</button>
            <button className="primary" onClick={shareAzure} disabled={busy}>Share minimized summary</button>
          </div>

          {azureContract && (
            <div className="meta meta-block">
              Mode: {azureContract.mode || 'stub'} • Enabled: {String(azureContract.azure_enabled)}
            </div>
          )}
          {azurePreview && (
            <div className="meta meta-block azure-preview">
              {(() => {
                const dm = azurePreview.data_minimization ?? azurePreview.payload?.data_minimization;
                const fp = dm?.payload_fingerprint;
                const summ = azurePreview.payload?.local_summary;
                const forbidden: string[] = [];
                if (dm) {
                  if (dm.raw_transcripts === false) forbidden.push("raw transcripts");
                  if (dm.vault_paths === false) forbidden.push("vault paths");
                  if (dm.forbidden_categories?.length) forbidden.push(...dm.forbidden_categories);
                }
                return (
                  <>
                    {fp && <div>Payload fingerprint: <code>{fp}</code></div>}
                    {forbidden.length > 0 && <div>Never sent: {forbidden.join(", ")}</div>}
                    {summ?.days_analyzed != null && <div>Payload: {summ.days_analyzed} days · {summ.files_scanned ?? "—"} files</div>}
                    {azurePreview.payload?.summary && <div>Payload: {azurePreview.payload.summary}</div>}
                    {azurePreview.note && <div className="note-line">{azurePreview.note}</div>}
                  </>
                );
              })()}
            </div>
          )}
          {azureResult && azureResult.share_url && (
            <div className="meta-block">
              <a className="share-link" href={azureResult.share_url} target="_blank" rel="noreferrer">
                Open shared clinical summary →
              </a>
            </div>
          )}
          {azureResult && !azureResult.share_url && azureResult.note && (
            <div className="meta meta-block">{azureResult.note}</div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">Skin photo ABCDE check (optional)</div>
        </div>
        <p className="card-lede">
          Upload a photo and get <strong>descriptive ABCDE-inspired features</strong> only —
          not a diagnosis, not a risk score. For any skin concern, see a dermatologist.
        </p>

        <details className="skin-guide">
          <summary>How to photograph a skin spot</summary>
          <ul>
            {(skinResult?.photo_guide ?? [
              'Use bright, diffuse, natural lighting (avoid harsh shadows and flash).',
              'Photograph the spot straight-on, filling most of the frame.',
              'Place a ruler or coin next to the spot for size reference.',
              'Keep the camera steady and in focus.',
            ]).map((g: string, i: number) => (
              <li key={i}>{g}</li>
            ))}
          </ul>
        </details>

        <div className="skin-upload">
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
                'Analyze this photo locally on this device? The image stays on your machine unless you enable external analysis. This is NOT a diagnosis.'
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
          {skinBusy && <div className="meta skin-busy">Analyzing image locally…</div>}
          {skinError && (
            <div className="skin-error">
              Could not analyze: {skinError}
            </div>
          )}
          {skinResult && !skinResult.error && (
            <div className="skin-result">
              <div><strong>Local ABCDE description</strong></div>
              <ul>
                {(skinResult.observations ?? []).map((obs: string, i: number) => (
                  <li key={i}>{obs}</li>
                ))}
              </ul>
              {skinResult.abcde_observations && (
                <div className="meta skin-meta">
                  diameter {skinResult.abcde_observations.diameter_px}px ·
                  asymmetry {skinResult.abcde_observations.asymmetry} ·
                  border {skinResult.abcde_observations.border_contrast} ·
                  colours {skinResult.abcde_observations.distinct_colors}
                </div>
              )}
              <div className="meta skin-meta">{skinResult.recommendation}</div>
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
      context={context}
      clinicalSummary={clinicalSummary}
      questions={questions}
    />
    </>
  );
}
