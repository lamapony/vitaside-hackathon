/* VitaSide — Connected Sources panel.
 *
 * Visualizes the multi-source collector integration: unified, local-first
 * intelligence from Obsidian notes + agent (Hermes) + wearables + Omi voice +
 * doctor-prescribed device (the proactive collection-window innovation).
 * Backed by /api/multi-source (live) with mock fallback.
 */
import { useEffect, useState } from "react";
import { FileText, Bot, Watch, Mic, Stethoscope, Lock, Sparkles } from "lucide-react";
import type { MultiSourceResponse } from "../api";
import { getJson } from "../api";

const SOURCE_ICONS: Record<string, React.ReactNode> = {
  notes: <FileText size={18} />,
  agent: <Bot size={18} />,
  wearables: <Watch size={18} />,
  omi: <Mic size={18} />,
  doctor_device: <Stethoscope size={18} />,
};

export function ConnectedSources() {
  const [data, setData] = useState<MultiSourceResponse | null>(null);

  useEffect(() => {
    let cancelled = false;
    getJson<MultiSourceResponse>("/api/multi-source")
      .then((d) => { if (!cancelled) setData(d); })
      .catch(() => { if (!cancelled) setData(null); });
    return () => { cancelled = true; };
  }, []);

  if (!data) return null;
  const sources = data.sources ?? [];
  const total = sources.reduce((a, s) => a + (s.events || 0), 0);

  return (
    <div className="card connected-sources">
      <div className="card-header">
        <div>
          <p className="eyebrow">Multi-source intelligence</p>
          <div className="card-title">Connected sources</div>
        </div>
        <span className="cs-total">{total} data points</span>
      </div>
      <p className="card-lede">
        Not just notes — unified patterns from all your personal sources. Every insight cites the source it came from.
      </p>

      <div className="cs-grid">
        {sources.map((s) => (
          <div className={`cs-source${s.proactive ? " proactive" : ""}`} key={s.id}>
            <div className="cs-source-icon">{SOURCE_ICONS[s.id] ?? <FileText size={18} />}</div>
            <div className="cs-source-body">
              <strong>{s.label}</strong>
              <span className="meta">{s.events} events · {s.status}</span>
            </div>
            {s.proactive && (
              <span className="cs-proactive-badge" title="Doctor-prescribed temporary device with proactive agent collection">
                <Sparkles size={11} /> proactive
              </span>
            )}
          </div>
        ))}
      </div>

      {data.doctor_device_active && (
        <div className="cs-doctor-note">
          <Stethoscope size={14} style={{ verticalAlign: -2, marginRight: 6 }} />
          Doctor-prescribed device active — agent proactively monitors the collection window and pre-assembles the visit packet.
        </div>
      )}

      <div className="cs-local">
        <Lock size={13} style={{ verticalAlign: -2, marginRight: 6 }} />
        All sources processed locally. Connect new sources anytime via MCP tools.
      </div>
    </div>
  );
}
