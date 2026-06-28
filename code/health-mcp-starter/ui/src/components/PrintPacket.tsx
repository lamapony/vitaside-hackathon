/* VitaSide — printable doctor visit packet.
 *
 * Shown only in print / Save-as-PDF (display:none on screen). Produces a clean
 * A4 handoff composed from the same data as the on-screen Doctor Handoff page:
 * clinical summary, trends, cited questions, and an honest disclaimer.
 *
 * Roadmap: Phase 3 — "PDF export (print CSS or weasyprint)". Pure frontend,
 * no backend dependency, works in demo mode too.
 */
import type { ClinicalSummary, Questions, UserContext, UserContextProfile } from "../api";

const DISCLAIMER =
  "Personal lifestyle patterns only — not a medical diagnosis. Always discuss these observations with a qualified clinician.";

const PREPARED_NOTE =
  "Prepared locally on your device from your own notes and wearables. N-of-1 patterns (single individual). Every claim is tied to a dated excerpt available in the app. No cloud used by default.";

type Props = {
  className?: string;
  visitDate: string;
  profile?: UserContextProfile;
  context?: UserContext;
  clinicalSummary?: ClinicalSummary | null;
  questions?: Questions;
};

function directionWord(dir?: string): string {
  if (dir === "up") return "Increasing";
  if (dir === "down") return "Decreasing";
  if (dir === "stable") return "Stable";
  return "—";
}

function pct(v?: number): string {
  if (v == null || Number.isNaN(v)) return "—";
  const sign = v > 0 ? "+" : "";
  return `${sign}${Math.round(v * 100)}%`;
}

function humanizeLabel(s: string): string {
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

export function PrintPacket({ className, visitDate, profile, context, clinicalSummary, questions }: Props) {
  const trends = clinicalSummary?.trends ?? [];
  const qs = questions?.questions ?? [];
  const name = profile?.display_name ?? "Patient";
  const conditions = (context?.conditions ?? []).map((c) => c.name ?? c.id).filter(Boolean);
  const medications = (context?.medications ?? [])
    .map((m) => `${m.name ?? m.id}${m.dose ? ` ${m.dose}` : ""}`)
    .filter(Boolean);

  return (
    <article className={`print-packet${className ? " " + className : ""}`}>
      <header className="pp-header">
        <div className="pp-brand">VitaSide</div>
        <div className="pp-title">
          <h1>Doctor Visit Preparation</h1>
          <p className="pp-sub">Visit date: {visitDate} · Prepared for {name}</p>
        </div>
        <div className="pp-conf">
          <span className="pp-conf-label">Confidence</span>
          <span className="pp-conf-value">Exploratory · N-of-1</span>
        </div>
      </header>

      <section className="pp-section">
        <h2 className="pp-h2">Patient context</h2>
        <p className="pp-small">
          {name}{profile?.age ? ` · ${profile.age}` : ""}{profile?.timezone ? ` · ${profile.timezone}` : ""}
        </p>
        {profile?.main_goal && <p className="pp-small"><strong>Goal:</strong> {profile.main_goal}</p>}
        {conditions.length > 0 && <p className="pp-small"><strong>Conditions:</strong> {conditions.join(", ")}</p>}
        {medications.length > 0 && <p className="pp-small"><strong>Medications:</strong> {medications.join(", ")}</p>}
        {profile?.doctor_notes && <p className="pp-small"><strong>Notes for clinician:</strong> {profile.doctor_notes}</p>}
      </section>

      <section className="pp-section">
        <h2 className="pp-h2">Clinical summary</h2>
        {clinicalSummary?.headline ? (
          <p className="pp-lede">{clinicalSummary.headline}</p>
        ) : (
          <p className="pp-lede pp-muted">No clinical summary available.</p>
        )}
        {clinicalSummary && (
          <p className="pp-meta">Window: {clinicalSummary.days_analyzed ?? 90} days · local analysis</p>
        )}

        {trends.length > 0 && (
          <table className="pp-trends">
            <thead>
              <tr>
                <th>Signal</th>
                <th>Direction</th>
                <th>Δ 14d</th>
                <th>Recent / prior</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {trends.map((t, i) => {
                const delta14 = t.delta ?? t.delta_14d;
                const recent = t.recent_14d ?? t.recent_freq;
                const prior = t.prior_14d ?? t.prior_freq;
                const label = t.label ?? t.signal ?? "—";
                return (
                  <tr key={`${label}-${i}`}>
                    <td>{humanizeLabel(label)}</td>
                    <td className="pp-center">{directionWord(t.direction)}</td>
                    <td className="pp-center">{delta14 != null ? pct(delta14) : "—"}</td>
                    <td className="pp-center">{recent != null && prior != null ? `${Math.round(recent * 100)}% / ${Math.round(prior * 100)}%` : "—"}</td>
                    <td className="pp-small">{t.detail ?? (t.unit ? t.unit : "")}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </section>

      <section className="pp-section pp-avoid-break">
        <h2 className="pp-h2">Questions to discuss with your clinician</h2>
        {qs.length > 0 ? (
          <ol className="pp-questions">
            {qs.map((q, i) => (
              <li key={i} className="pp-q">
                <div className="pp-q-text">{q.question}</div>
                {q.evidence && <div className="pp-q-evidence">{q.evidence}</div>}
              </li>
            ))}
          </ol>
        ) : (
          <p className="pp-muted">No questions generated.</p>
        )}
      </section>

      <section className="pp-section">
        <h2 className="pp-h2">How this was prepared</h2>
        <p className="pp-small">{PREPARED_NOTE}</p>
      </section>

      <footer className="pp-footer">
        <p>{DISCLAIMER}</p>
        <p className="pp-small pp-muted">Generated by VitaSide · {visitDate} · processed locally</p>
      </footer>
    </article>
  );
}
