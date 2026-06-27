import { useEffect, useState } from "react";
import { GitCompare } from "lucide-react";
import {
  DEMO_SIGNALS,
  DemoSignal,
  Narrative,
  N1Compare,
  SmartAnalysis,
  getJson,
  signalLabel
} from "../api";

type Props = {
  smart?: SmartAnalysis;
  narrative?: Narrative;
};

export function Smart({ smart, narrative }: Props) {
  const attention = smart?.attention_now ?? [];
  const weekdayEffects = smart?.weekday_effects ?? [];
  const baselines = smart?.personal_baselines?.signals ?? {};
  const baselineEntries = Object.entries(baselines).slice(0, 8);
  const regimes = buildRegimeCards(smart);

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Personal intelligence layer</p>
          <h1>Smart analysis</h1>
        </div>
        <p>Baselines, weekday effects, and attention alerts — grounded in your history, not population averages.</p>
      </div>

      <N1CompareCard />

      {smart?.summary && (
        <div className="stats-row compact">
          <Stat label="Baseline signals" value={smart.summary.baseline_signals ?? "—"} />
          <Stat label="Weekday patterns" value={smart.summary.weekday_patterns ?? "—"} />
          <Stat label="Attention items" value={smart.summary.attention_items ?? attention.length} />
          <Stat label="Recent anomalies" value={smart.summary.recent_anomalies ?? "—"} />
        </div>
      )}

      <div className="section-heading">
        <h2>Regime signals</h2>
        <p>Lightweight state view built from attention items, baselines, and weekday effects.</p>
      </div>

      <div className="regime-grid">
        {regimes.map((regime) => (
          <article className={`regime-card ${regime.tone}`} key={regime.title}>
            <span>{regime.label}</span>
            <strong>{regime.title}</strong>
            <p>{regime.detail}</p>
          </article>
        ))}
      </div>

      <div className="section-heading">
        <h2>Attention now</h2>
        <p>What needs attention this week — each item carries dated evidence.</p>
      </div>

      <div className="insight-grid">
        {attention.map((item, index) => (
          <article className="insight-card attention-card" key={`${item.headline}-${index}`}>
            <span className="rank">P{item.priority ?? index + 1}</span>
            <h3>{item.headline}</h3>
            <p>{item.detail}</p>
            {item.evidence_quote && (
              <blockquote>
                <small>{item.evidence_date}</small>
                {item.evidence_quote}
              </blockquote>
            )}
            {item.action && <p className="action-line">{item.action}</p>}
          </article>
        ))}
        {!attention.length && (
          <article className="insight-card">
            <h3>No urgent attention signals</h3>
            <p>Your recent patterns are within personal baseline bands.</p>
          </article>
        )}
      </div>

      {narrative?.narrative && (
        <div className="soft-card narrative-block">
          <p className="eyebrow">Local narrative · {narrative.locale ?? "ru"}</p>
          <h2>Your story from the data</h2>
          {narrative.narrative.split("\n\n").map((paragraph, index) => (
            <p key={index} className="narrative-paragraph">
              {paragraph.replace(/\*\*/g, "")}
            </p>
          ))}
          {narrative.evidence_map && narrative.evidence_map.length > 0 && (
            <div className="evidence-map">
              <h3>Evidence map</h3>
              <ul>
                {narrative.evidence_map.map((item, index) => (
                  <li key={`${item.claim}-${index}`}>
                    <strong>{item.claim}</strong>
                    <span>
                      {item.source}
                      {item.date ? ` · ${item.date}` : ""}
                    </span>
                    {item.excerpt && <blockquote>{item.excerpt}</blockquote>}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="smart-layout">
        <div className="soft-card">
          <p className="eyebrow">Weekday effects</p>
          <h2>When signals spike</h2>
          <div className="weekday-list">
            {weekdayEffects.slice(0, 6).map((effect) => (
              <div className="weekday-row" key={`${effect.signal}-${effect.weekday}`}>
                <div>
                  <strong>{effect.signal.replace(/_/g, " ")}</strong>
                  <span>
                    {effect.weekday_name_ru ?? effect.weekday_name} · {effect.lift.toFixed(1)}× lift
                  </span>
                </div>
                <div className="bar-track">
                  <span style={{ width: `${Math.min(effect.lift / 2, 1) * 100}%` }} />
                </div>
                <small>
                  {Math.round(effect.weekday_freq * 100)}% on day vs {Math.round(effect.overall_freq * 100)}% overall
                </small>
              </div>
            ))}
            {!weekdayEffects.length && <p className="empty">No strong weekday patterns detected.</p>}
          </div>
        </div>

        <div className="soft-card">
          <p className="eyebrow">Personal baselines</p>
          <h2>Your frequency bands</h2>
          <div className="bar-list">
            {baselineEntries.map(([signal, baseline]) => (
              <div className="bar-row" key={signal}>
                <div>
                  <span>{signal.replace(/_/g, " ")}</span>
                  <strong>
                    {Math.round(baseline.mean_freq * 100)}%
                    {baseline.trend && baseline.trend !== "insufficient_data" ? ` · ${baseline.trend}` : ""}
                  </strong>
                </div>
                <div className="bar-track">
                  <span style={{ width: `${Math.min(baseline.mean_freq * 100, 100)}%` }} />
                </div>
                <small>
                  Band {Math.round(baseline.band_low * 100)}%–{Math.round(baseline.band_high * 100)}%
                </small>
              </div>
            ))}
            {!baselineEntries.length && <p className="empty">Not enough data for personal baselines yet.</p>}
          </div>
        </div>
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function buildRegimeCards(smart?: SmartAnalysis) {
  const summary = smart?.summary;
  const attention = smart?.attention_now ?? [];
  const weekday = smart?.weekday_effects ?? [];
  const baselines = smart?.personal_baselines?.signals ?? {};
  const baselineCount = Object.keys(baselines).length;
  return [
    {
      label: "Current state",
      title: attention.length ? "Watch week" : "Stable band",
      detail: attention.length
        ? `${attention.length} recent item${attention.length === 1 ? "" : "s"} outside the calm baseline.`
        : "Recent signals are not showing an urgent deviation from personal history.",
      tone: attention.length ? "watch" : "stable"
    },
    {
      label: "Rhythm",
      title: weekday.length ? "Weekday pattern detected" : "No strong weekday rhythm",
      detail: weekday.length
        ? `${weekday[0].weekday_name_ru ?? weekday[0].weekday_name} has the strongest ${weekday[0].signal.replace(/_/g, " ")} lift.`
        : "No weekday effect is strong enough to highlight yet.",
      tone: weekday.length ? "watch" : "neutral"
    },
    {
      label: "Baseline depth",
      title: `${baselineCount || summary?.baseline_signals || 0} personal bands`,
      detail: "VitaSide compares against your own tracked days before using generic expectations.",
      tone: baselineCount >= 3 ? "stable" : "neutral"
    }
  ];
}

function N1CompareCard() {
  const [exposure, setExposure] = useState<DemoSignal>("stress");
  const [outcome, setOutcome] = useState<DemoSignal>("mood_low");
  const [compare, setCompare] = useState<N1Compare | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(undefined);
      try {
        const data = await getJson<N1Compare>(
          `/api/n1-compare?exposure_signal=${encodeURIComponent(exposure)}&outcome_signal=${encodeURIComponent(outcome)}&window_days=7`
        );
        if (!cancelled) setCompare(data);
      } catch (err) {
        if (!cancelled) {
          setCompare(null);
          setError(err instanceof Error ? err.message : String(err));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [exposure, outcome]);

  return (
    <div className="soft-card n1-compare-card">
      <div className="card-header">
        <div>
          <p className="eyebrow">N-of-1 compare</p>
          <h2>Exposure weeks vs control weeks</h2>
        </div>
        <GitCompare size={18} />
      </div>

      <div className="n1-controls">
        <label>
          <span className="meta">Exposure signal</span>
          <select value={exposure} onChange={(e) => setExposure(e.target.value as DemoSignal)}>
            {DEMO_SIGNALS.map((signal) => (
              <option key={signal} value={signal}>
                {signalLabel(signal)}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span className="meta">Outcome signal</span>
          <select value={outcome} onChange={(e) => setOutcome(e.target.value as DemoSignal)}>
            {DEMO_SIGNALS.filter((s) => s !== exposure).map((signal) => (
              <option key={signal} value={signal}>
                {signalLabel(signal)}
              </option>
            ))}
          </select>
        </label>
      </div>

      {loading && <div className="meta">Comparing periods…</div>}

      {!loading && error && (
        <div className="meta">N-of-1 compare unavailable ({error}). Backend endpoint may still be loading.</div>
      )}

      {!loading && !error && compare && (
        <div className="n1-results">
          {(compare.headline || compare.summary || compare.interpretation) && (
            <p className="n1-headline">{compare.headline ?? compare.summary ?? compare.interpretation}</p>
          )}
          <div className="n1-stats">
            {(compare.exposure_days ?? compare.exposure_weeks) != null && (
              <div className="stat-card">
                <span>Exposure days</span>
                <strong>{compare.exposure_days ?? compare.exposure_weeks}</strong>
              </div>
            )}
            {(compare.control_days ?? compare.control_weeks) != null && (
              <div className="stat-card">
                <span>Control days</span>
                <strong>{compare.control_days ?? compare.control_weeks}</strong>
              </div>
            )}
            {(compare.lift_ratio ?? compare.lift) != null && (
              <div className="stat-card">
                <span>Lift</span>
                <strong>{(compare.lift_ratio ?? compare.lift ?? 0).toFixed(2)}×</strong>
              </div>
            )}
            {compare.risk_difference != null && (
              <div className="stat-card">
                <span>Risk diff</span>
                <strong>{Math.round(compare.risk_difference * 100)}pp</strong>
              </div>
            )}
          </div>
          {(compare.exposure_outcome_rate != null || compare.control_outcome_rate != null) && (
            <div className="n1-rates">
              {compare.exposure_outcome_rate != null && (
                <span>
                  {signalLabel(outcome)} in exposure weeks: {Math.round(compare.exposure_outcome_rate * 100)}%
                </span>
              )}
              {compare.control_outcome_rate != null && (
                <span>
                  {signalLabel(outcome)} in control weeks: {Math.round(compare.control_outcome_rate * 100)}%
                </span>
              )}
            </div>
          )}
          {(compare.ci_95?.low != null || compare.ci_low != null) && (compare.ci_95?.high != null || compare.ci_high != null) && (
            <div className="meta">
              95% CI: {(compare.ci_95?.low ?? compare.ci_low ?? 0).toFixed(2)} – {(compare.ci_95?.high ?? compare.ci_high ?? 0).toFixed(2)}
            </div>
          )}
          {compare.p_value != null && <div className="meta">Exploratory p-value: {compare.p_value}</div>}
          {compare.confidence && <div className="meta">Confidence: {compare.confidence}</div>}
          {compare.example?.excerpt && (
            <blockquote>
              <small>{compare.example.date}</small>
              {compare.example.excerpt}
            </blockquote>
          )}
          {compare.note && <div className="meta">{compare.note}</div>}
        </div>
      )}
    </div>
  );
}
