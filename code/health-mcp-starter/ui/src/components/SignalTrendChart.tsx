/* VitaSide — signal frequency trend chart (Roadmap Phase 3: rich inline charts).
 *
 * Dependency-free SVG line chart: weekly share of days with each signal over
 * the timeline window. Derived from the same TimelineEntry[] the page already
 * loads, so it works in both live and demo mode. When a specific signal is
 * active, plots that signal; otherwise plots the top 2–3 signals.
 */
import { useMemo } from "react";
import type { TimelineEntry } from "../api";

const SIGNAL_LABELS: Record<string, string> = {
  sleep: "Sleep",
  stress: "Stress",
  mood_low: "Low mood",
  mood_good: "Good mood",
  exercise: "Activity",
  caffeine_alcohol: "Caffeine / alcohol",
  symptom_pain: "Pain / symptom",
  social: "Social",
};

const COLORS = ["var(--accent)", "var(--warning)", "#5b8a7d"];

type Props = { entries: TimelineEntry[]; activeSignal: string };

function parseDate(s: string): number {
  return new Date(`${s}T00:00:00Z`).getTime();
}

type Model = {
  weekCount: number;
  plotSignals: string[];
  series: number[][];
  maxFrac: number;
  firstDate: string;
  lastDate: string;
};

export function SignalTrendChart({ entries, activeSignal }: Props) {
  const model = useMemo<Model | null>(() => {
    if (!entries.length) return null;
    const byDate = new Map(entries.map((e) => [e.date, e]));
    const dates = entries.map((e) => e.date).sort();
    const start = parseDate(dates[0]);
    const end = parseDate(dates[dates.length - 1]);
    if (!start || !end || end < start) return null;

    const dayCount = Math.round((end - start) / 86400000) + 1;
    const days: (TimelineEntry | undefined)[] = [];
    for (let i = 0; i < dayCount; i++) {
      const d = new Date(start);
      d.setUTCDate(d.getUTCDate() + i);
      days.push(byDate.get(d.toISOString().slice(0, 10)));
    }

    const weekCount = Math.max(1, Math.ceil(dayCount / 7));
    const bins: { total: number; counts: Map<string, number> }[] = [];
    for (let w = 0; w < weekCount; w++) {
      const counts = new Map<string, number>();
      let total = 0;
      for (let i = 0; i < 7; i++) {
        const idx = w * 7 + i;
        if (idx >= dayCount) break;
        total++;
        const e = days[idx];
        if (e) e.signals.forEach((s) => counts.set(s, (counts.get(s) ?? 0) + 1));
      }
      bins.push({ total: total || 1, counts });
    }

    const totals = new Map<string, number>();
    entries.forEach((e) => e.signals.forEach((s) => totals.set(s, (totals.get(s) ?? 0) + 1)));
    const topSignals = [...totals.entries()].sort((a, b) => b[1] - a[1]).map((x) => x[0]);
    const plotSignals = activeSignal !== "all" ? [activeSignal] : topSignals.slice(0, 3);

    const series = plotSignals.map((sig) => bins.map((b) => (b.counts.get(sig) ?? 0) / b.total));
    let maxFrac = 0;
    series.forEach((s) => s.forEach((v) => { if (v > maxFrac) maxFrac = v; }));
    if (maxFrac < 0.1) maxFrac = 0.1;

    return { weekCount, plotSignals, series, maxFrac, firstDate: dates[0], lastDate: dates[dates.length - 1] };
  }, [entries, activeSignal]);

  if (!model) return null;

  const W = 600;
  const H = 140;
  const padL = 8;
  const padR = 8;
  const padT = 10;
  const padB = 22;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;
  const xAt = (i: number) => padL + (model.weekCount <= 1 ? 0 : (i / (model.weekCount - 1)) * plotW);
  const yAt = (v: number) => padT + plotH - (v / model.maxFrac) * plotH;

  return (
    <div className="signal-trend-chart">
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label="Signal frequency trend over time">
        {[0, 0.25, 0.5, 0.75, 1].map((g, i) => {
          const y = padT + plotH - g * plotH;
          return <line key={i} x1={padL} x2={W - padR} y1={y} y2={y} stroke="var(--line-soft)" strokeWidth={1} />;
        })}
        {model.series.map((s, si) => {
          const pts = s.map((v, i) => `${xAt(i).toFixed(1)},${yAt(v).toFixed(1)}`).join(" ");
          return (
            <polyline
              key={si}
              points={pts}
              fill="none"
              stroke={COLORS[si % COLORS.length]}
              strokeWidth={2}
              strokeLinejoin="round"
              strokeLinecap="round"
            />
          );
        })}
      </svg>
      <div className="signal-trend-legend">
        {model.plotSignals.map((sig, i) => (
          <span key={sig}>
            <i style={{ background: COLORS[i % COLORS.length] }} /> {SIGNAL_LABELS[sig] ?? sig}
          </span>
        ))}
        <span className="signal-trend-range">{model.firstDate} → {model.lastDate} · weekly frequency</span>
      </div>
    </div>
  );
}
