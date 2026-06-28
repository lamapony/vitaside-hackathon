import { ConditionPack, ConditionReport } from "../api";

type Props = {
  packs: ConditionPack[];
  selected: string;
  setSelected: (id: string) => void;
  report?: ConditionReport;
};

function humanize(s: string): string {
  const known: Record<string, string> = {
    avg_intensity: "Average intensity",
    duration_h: "Duration (h)",
    days_free: "Days free",
    symptom_pain: "Pain / symptom",
    headache: "Headache",
    episodes: "Episodes",
    med_response: "Med response",
  };
  return known[s] ?? s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function Condition({ packs, selected, setSelected, report }: Props) {
  return (
    <section>
      <div className="section-heading">
        <h1>Condition tracking</h1>
        <p>Focused self-monitoring packs: symptoms, meds, triggers and visit questions.</p>
      </div>

      <div className="toolbar">
        <label>
          Pack
          <select value={selected} onChange={(event) => setSelected(event.target.value)}>
            {packs.map((pack) => (
              <option key={pack.id} value={pack.id}>{pack.name}</option>
            ))}
          </select>
        </label>
      </div>

      {report && (
        <div className="condition-layout">
          <div className="soft-card">
            <p className="eyebrow">Condition pack</p>
            <h2>{report.condition_name}</h2>
            <p>{report.days_analyzed} days analyzed. Patterns only — not diagnosis.</p>
          </div>

          <div className="soft-card">
            <h3>What we track</h3>
            <div className="bar-list">
              {report.track_items.map((item) => (
                <div className="bar-row" key={item.id}>
                  <div>
                    <strong>{item.label}</strong>
                    <span>{item.days_with_signal} days</span>
                  </div>
                  <div className="bar-track">
                    <span style={{ width: `${Math.min(item.frequency * 100, 100)}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="soft-card">
            <h3>Metrics</h3>
            <div className="metric-list">
              {report.metrics.map((metric) => (
                <div className="metric-card" key={metric.id}>
                  <strong>{metric.value ?? "—"} {metric.unit ?? ""}</strong>
                  <span>{humanize(metric.id)}</span>
                  {metric.note && <p>{metric.note}</p>}
                </div>
              ))}
            </div>
          </div>

          <div className="soft-card">
            <h3>For your doctor</h3>
            <ul className="doctor-list">
              {(report.doctor_focus ?? []).map((item) => <li key={item}>{item}</li>)}
            </ul>
            {!!report.citations?.length && (
              <>
                <h3>Evidence snippets</h3>
                {report.citations.slice(0, 4).map((citation) => (
                  <blockquote key={`${citation.date}-${citation.signal}`}>
                    <small>{citation.date} · {humanize(citation.signal)}</small>
                    {citation.excerpt}
                  </blockquote>
                ))}
              </>
            )}
          </div>
        </div>
      )}

      {!report && (
        <div className="soft-card">
          <p className="meta">Loading condition report…</p>
        </div>
      )}

      <p className="disclaimer">{report?.disclaimer ?? "Patterns for self-awareness — not medical diagnosis."}</p>
    </section>
  );
}
