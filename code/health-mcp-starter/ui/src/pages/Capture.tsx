/* VitaSide — Capture page.
 *
 * Two manual-capture features (pure frontend, no backend changes):
 *  1. Add a document for analysis — paste or upload .txt/.md/.csv; VitaSide
 *     extracts dated signal observations locally and can add a summary to notes.
 *  2. Voice note — dictation via the Web Speech API; save the transcript as a note.
 *
 * Notes are saved through the existing /api/manual-logs endpoint (works in live
 * and demo mode). Document analysis happens entirely in the browser.
 */
import { useState } from "react";
import { FileUp, Mic, Square, Sparkles, Plus, ShieldAlert, CheckCircle2 } from "lucide-react";
import type { ManualLog, UserContext, UserContextResponse } from "../api";
import { postJson } from "../api";
import { analyzeDocument, SAMPLE_DOCUMENT, signalLabel, type DocumentAnalysis } from "../lib/documentAnalysis";
import { useVoiceInput } from "../hooks/useVoiceInput";

type Props = {
  onContextChange: (ctx: UserContext) => void;
};

export function Capture({ onContextChange }: Props) {
  return (
    <section className="page-grid fade-in">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Manual capture</p>
          <h1>Add data</h1>
        </div>
        <p>Add a document for local analysis, or dictate a note. Everything is processed on your device.</p>
      </div>

      <DocumentCard onContextChange={onContextChange} />
      <VoiceCard onContextChange={onContextChange} />
    </section>
  );
}

function DocumentCard({ onContextChange }: { onContextChange: (ctx: UserContext) => void }) {
  const [text, setText] = useState("");
  const [filename, setFilename] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<DocumentAnalysis | null>(null);
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState(false);

  function runAnalysis() {
    if (!text.trim()) return;
    setAnalysis(analyzeDocument(text));
    setSaved(false);
  }

  function onFile(file: File) {
    setFilename(file.name);
    const reader = new FileReader();
    reader.onload = () => {
      const content = String(reader.result ?? "");
      setText(content);
      setAnalysis(analyzeDocument(content));
      setSaved(false);
    };
    reader.readAsText(file);
  }

  async function addToNotes() {
    if (!analysis) return;
    setBusy(true);
    try {
      const top = analysis.signalCounts.slice(0, 4);
      const summary = `Document${filename ? ` (${filename})` : ""}: ${analysis.totalSignals} signal hits across ${analysis.datedEntries} dated entries. Top: ${analysis.signalCounts.slice(0, 3).map((s) => s.label).join(", ") || "none"}.`;
      const payload: Partial<ManualLog> & { text: string } = {
        type: "document",
        text: summary,
        tags: top.map((s) => s.signal),
      };
      const result = await postJson<UserContextResponse>("/api/manual-logs", payload);
      onContextChange(result.context);
      setSaved(true);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <p className="eyebrow">Document analysis</p>
          <div className="card-title">Add a document for analysis</div>
        </div>
        <FileUp size={18} />
      </div>
      <p className="card-lede">
        Paste text or upload a .txt / .md / .csv file (a health journal, export, or clinical notes).
        VitaSide extracts dated signals locally — nothing is uploaded.
      </p>

      <textarea
        className="doc-textarea"
        placeholder="Paste your document here, or load a sample…"
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={6}
      />

      <div className="button-row capture-actions">
        <label className="secondary file-label">
          <FileUp size={16} /> Upload file
          <input
            type="file"
            accept=".txt,.md,.csv,.json,text/plain,text/markdown"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) onFile(f); }}
          />
        </label>
        <button type="button" className="secondary" onClick={() => { setText(SAMPLE_DOCUMENT); setFilename("sample-journal.txt"); setAnalysis(analyzeDocument(SAMPLE_DOCUMENT)); setSaved(false); }}>
          Load sample
        </button>
        <button type="button" className="primary" onClick={runAnalysis} disabled={!text.trim()}>
          <Sparkles size={16} /> Analyze
        </button>
      </div>

      {filename && <p className="meta">Loaded: {filename} · {text.length} chars</p>}

      {analysis && (
        <div className="doc-analysis">
          <div className="stats-row compact">
            <div className="stat-card"><span>Dated entries</span><strong>{analysis.datedEntries}</strong></div>
            <div className="stat-card"><span>Signal hits</span><strong>{analysis.totalSignals}</strong></div>
            <div className="stat-card"><span>Distinct signals</span><strong>{analysis.signalCounts.length}</strong></div>
          </div>

          {analysis.signalCounts.length > 0 && (
            <div className="chips">
              {analysis.signalCounts.map((s) => (
                <span key={s.signal} className="chip chip-muted">{s.label} · {s.count}</span>
              ))}
            </div>
          )}

          {analysis.observations.length > 0 && (
            <div className="doc-observations">
              <p className="eyebrow">Extracted observations</p>
              {analysis.observations.map((obs, i) => (
                <div className="doc-obs" key={i}>
                  <div className="doc-obs-head">
                    <strong>{obs.date === "undated" ? "Undated" : obs.date}</strong>
                    <div className="signal-stack">
                      {obs.signals.map((s) => (
                        <span key={s} className="signal">{signalLabel(s)}</span>
                      ))}
                    </div>
                  </div>
                  {obs.excerpt && <div className="evidence">{obs.excerpt}</div>}
                </div>
              ))}
            </div>
          )}

          {analysis.observations.length === 0 && (
            <p className="meta">No dated signal observations found. Add dates (YYYY-MM-DD) and symptom words for best results.</p>
          )}

          <button type="button" className="primary" onClick={addToNotes} disabled={busy || analysis.observations.length === 0}>
            <Plus size={16} /> {busy ? "Saving…" : "Add summary to notes"}
          </button>
          {saved && <p className="meta meta-block"><CheckCircle2 size={13} style={{ verticalAlign: -2, marginRight: 4 }} />Summary added to your notes.</p>}
        </div>
      )}
    </div>
  );
}

function VoiceCard({ onContextChange }: { onContextChange: (ctx: UserContext) => void }) {
  const voice = useVoiceInput();
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState(false);

  async function saveNote() {
    if (!voice.transcript.trim()) return;
    setBusy(true);
    try {
      const result = await postJson<UserContextResponse>("/api/manual-logs", {
        type: "note",
        text: voice.transcript.trim(),
        tags: ["voice"],
      });
      onContextChange(result.context);
      voice.reset();
      setSaved(true);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <p className="eyebrow">Voice note</p>
          <div className="card-title">Dictate a note</div>
        </div>
        <Mic size={18} />
      </div>
      <p className="card-lede">
        Tap the mic and speak. Your words appear below — edit if needed, then save as a note.
      </p>

      {!voice.supported && (
        <p className="meta skin-error">Voice input is not supported in this browser. Try Chrome or Edge.</p>
      )}

      <div className="voice-controls">
        {voice.listening ? (
          <button type="button" className="primary voice-stop" onClick={voice.stop}>
            <Square size={16} /> Stop listening
          </button>
        ) : (
          <button type="button" className="primary voice-mic" onClick={voice.start} disabled={!voice.supported}>
            <Mic size={16} /> {voice.transcript ? "Continue" : "Start dictation"}
          </button>
        )}
        {voice.listening && <span className="voice-pulse">listening…</span>}
      </div>

      {voice.error && <p className="meta skin-error">{voice.error}</p>}

      <textarea
        className="doc-textarea"
        placeholder="Your dictation appears here…"
        value={voice.transcript + (voice.interim ? ` ${voice.interim}` : "")}
        onChange={(e) => voice.setTranscript(e.target.value)}
        rows={4}
      />

      <div className="button-row">
        <button type="button" className="secondary" onClick={voice.reset} disabled={!voice.transcript && !voice.interim}>
          Clear
        </button>
        <button type="button" className="primary" onClick={saveNote} disabled={busy || !voice.transcript.trim()}>
          <Plus size={16} /> {busy ? "Saving…" : "Save as note"}
        </button>
      </div>

      {saved && <p className="meta meta-block"><CheckCircle2 size={13} style={{ verticalAlign: -2, marginRight: 4 }} />Note saved.</p>}

      <p className="meta voice-notice">
        <ShieldAlert size={13} style={{ verticalAlign: -2, marginRight: 4 }} />
        Browser speech recognition may use the network. A fully on-device voice model is a future option.
      </p>
    </div>
  );
}
