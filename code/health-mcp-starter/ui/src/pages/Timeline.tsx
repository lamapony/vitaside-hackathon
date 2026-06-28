import { useMemo, useState } from "react";
import { CalendarDays, Filter, Quote, TrendingUp } from "lucide-react";
import { TimelineEntry } from "../api";
import { SignalTrendChart } from "../components/SignalTrendChart";

const SIGNAL_LABELS: Record<string, string> = {
  sleep: "Sleep",
  stress: "Stress",
  mood_low: "Low mood",
  mood_good: "Good mood",
  exercise: "Activity",
  caffeine_alcohol: "Caffeine / alcohol",
  symptom_pain: "Pain / symptom",
  social: "Social"
};

type Props = {
  entries: TimelineEntry[];
  activeSignal: string;
  setActiveSignal: (signal: string) => void;
};

export function Timeline({ entries, activeSignal, setActiveSignal }: Props) {
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const signals = Array.from(new Set(entries.flatMap((entry) => entry.signals))).sort();
  const filtered =
    activeSignal === "all"
      ? entries
      : entries.filter((entry) => entry.signals.includes(activeSignal));
  const selected = filtered.find((entry) => entry.date === selectedDate) ?? filtered[filtered.length - 1];
  const mostCommon = useMemo(() => {
    const counts = new Map<string, number>();
    entries.forEach((entry) => entry.signals.forEach((signal) => counts.set(signal, (counts.get(signal) ?? 0) + 1)));
    return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 3);
  }, [entries]);
  const calendarWeeks = useMemo(() => buildCalendarWeeks(filtered), [filtered]);

  return (
    <section className="fade-in">
      <header className="page-header">
        <div>
          <p className="eyebrow">Day by day</p>
          <h1>Timeline</h1>
          <p className="lede">
            Signals from your notes — with date and text excerpt. Filter to spot patterns.
          </p>
        </div>
      </header>

      <div className="timeline-v2-summary">
        <div className="stat-card">
          <span>Tracked days</span>
          <strong>{entries.length}</strong>
        </div>
        <div className="stat-card">
          <span>Visible days</span>
          <strong>{filtered.length}</strong>
        </div>
        <div className="stat-card">
          <span>Top signal</span>
          <strong>{mostCommon[0] ? SIGNAL_LABELS[mostCommon[0][0]] || mostCommon[0][0] : "—"}</strong>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <p className="eyebrow">Signal trend</p>
            <div className="card-title">Weekly frequency over time</div>
          </div>
          <TrendingUp size={18} />
        </div>
        <SignalTrendChart entries={entries} activeSignal={activeSignal} />
        <div className="meta" style={{ marginTop: 6 }}>
          Share of days per week with each signal — derived from your timeline entries.
        </div>
      </div>

      <div className="card timeline-filter-card">
        <div className="card-header">
          <div>
            <p className="eyebrow">Timeline v2</p>
            <div className="card-title">Heatmap + citation drill-down</div>
          </div>
          <Filter size={18} />
        </div>
        <div className="timeline-filter-pills">
          <button
            type="button"
            className={activeSignal === "all" ? "pill active" : "pill"}
            onClick={() => setActiveSignal("all")}
          >
            All
          </button>
          {signals.map((sig) => (
            <button
              key={sig}
              type="button"
              className={activeSignal === sig ? "pill active" : "pill"}
              onClick={() => setActiveSignal(sig)}
            >
              {SIGNAL_LABELS[sig] || sig}
            </button>
          ))}
        </div>
      </div>

      <div className="timeline-v2-layout">
        <div className="card timeline-heatmap-card">
          <div className="card-header">
            <div>
              <p className="eyebrow">Calendar heatmap</p>
              <div className="card-title">Signal density over time</div>
            </div>
            <CalendarDays size={18} />
          </div>
          {filtered.length === 0 && <div className="meta">No entries for this filter.</div>}
          {filtered.length > 0 && (
            <div className="calendar-heatmap" aria-label="Timeline heatmap">
              <div className="calendar-weekday">M</div>
              <div className="calendar-weekday">T</div>
              <div className="calendar-weekday">W</div>
              <div className="calendar-weekday">T</div>
              <div className="calendar-weekday">F</div>
              <div className="calendar-weekday">S</div>
              <div className="calendar-weekday">S</div>
              {calendarWeeks.flat().map((entry, index) =>
                entry ? (
                  <button
                    key={entry.date}
                    type="button"
                    className={entry.date === selected?.date ? "heatmap-day active" : "heatmap-day"}
                    data-intensity={Math.min(entry.signals.length, 4)}
                    onClick={() => setSelectedDate(entry.date)}
                    aria-label={`${entry.date}: ${entry.signals.map((sig) => SIGNAL_LABELS[sig] || sig).join(", ")}`}
                  >
                    <span>{Number(entry.date.slice(-2))}</span>
                  </button>
                ) : (
                  <span key={`empty-${index}`} className="heatmap-day empty" />
                )
              )}
            </div>
          )}
          <div className="timeline-legend">
            <span>Fewer signals</span>
            <i data-intensity="1" />
            <i data-intensity="2" />
            <i data-intensity="3" />
            <i data-intensity="4" />
            <span>More</span>
          </div>
        </div>

        <aside className="card citation-drill">
          <div className="card-header">
            <div>
              <p className="eyebrow">Citation drill</p>
              <div className="card-title">{selected?.date ?? "Select a day"}</div>
            </div>
            <Quote size={18} />
          </div>
          {selected ? (
            <>
              <div className="signal-stack">
                {selected.signals.map((sig) => (
                  <span key={sig} className="signal">
                    {SIGNAL_LABELS[sig] || sig}
                  </span>
                ))}
              </div>
              {selected.sleep_quality && selected.sleep_quality !== "unknown" && (
                <div className="meta">Sleep: {selected.sleep_quality}</div>
              )}
              {selected.low_quality_excerpt && (
                <div className="meta warn">Low parser confidence — excerpt may be noisy (PP-05).</div>
              )}
              {selected.parser_confidence != null && (
                <div className="meta">Parser confidence: {(selected.parser_confidence * 100).toFixed(0)}%</div>
              )}
              {selected.snippet ? (
                <blockquote className="evidence">{selected.snippet}</blockquote>
              ) : (
                <div className="meta">No citation for this day.</div>
              )}
            </>
          ) : (
            <div className="meta">Pick a day on the calendar.</div>
          )}
        </aside>
      </div>

      <div className="card timeline-list-card">
        <div className="card-header">
          <div>
            <p className="eyebrow">Detailed list</p>
            <div className="card-title">Dated observations</div>
          </div>
        </div>
        {filtered.length === 0 && <div className="meta">No entries for this filter.</div>}
        {filtered.map((entry, idx) => (
          <div key={idx} className="timeline-item">
            <div className="timeline-item-head">
              <strong>{entry.date}</strong>
              {entry.sleep_quality && entry.sleep_quality !== "unknown" && (
                <span className="meta">Sleep: {entry.sleep_quality}</span>
              )}
            </div>
            <div className="signal-stack">
              {entry.signals.map((sig) => (
                <span key={sig} className="signal">
                  {SIGNAL_LABELS[sig] || sig}
                </span>
              ))}
            </div>
            {entry.snippet && <div className="evidence">{entry.snippet}</div>}
          </div>
        ))}
      </div>
    </section>
  );
}

function buildCalendarWeeks(entries: TimelineEntry[]) {
  const byDate = new Map(entries.map((entry) => [entry.date, entry]));
  const dates = entries.map((entry) => entry.date).sort();
  if (!dates.length) return [];
  const start = parseDate(dates[0]);
  const end = parseDate(dates[dates.length - 1]);
  if (!start || !end) return [];
  const cursor = new Date(start);
  const mondayOffset = (cursor.getDay() + 6) % 7;
  cursor.setDate(cursor.getDate() - mondayOffset);
  const weeks: Array<Array<TimelineEntry | null>> = [];
  while (cursor <= end) {
    const week: Array<TimelineEntry | null> = [];
    for (let day = 0; day < 7; day += 1) {
      const key = cursor.toISOString().slice(0, 10);
      week.push(byDate.get(key) ?? null);
      cursor.setDate(cursor.getDate() + 1);
    }
    weeks.push(week);
  }
  return weeks;
}

function parseDate(value: string) {
  const date = new Date(`${value}T00:00:00`);
  return Number.isNaN(date.getTime()) ? null : date;
}
