/* VitaSide — Frame Glasses panel.
 *
 * Surfaces the Brilliant Labs Frame glasses integration (~/vitaside): vision
 * lifestyle capture → tags → patterns → doctor recommendation. Backed by
 * /api/frame-glasses (live, reads the real ~/vitaside/data) with mock fallback.
 */
import { useEffect, useState } from "react";
import { Glasses, Camera, Activity, MapPin, Lightbulb } from "lucide-react";
import type { FrameGlassesResponse } from "../api";
import { getJson } from "../api";

function humanizeTag(t: string): string {
  return t.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function FrameGlasses() {
  const [data, setData] = useState<FrameGlassesResponse | null>(null);

  useEffect(() => {
    let cancelled = false;
    getJson<FrameGlassesResponse>("/api/frame-glasses")
      .then((d) => { if (!cancelled) setData(d); })
      .catch(() => { if (!cancelled) setData(null); });
    return () => { cancelled = true; };
  }, []);

  if (!data || !data.connected) return null;

  const topTags = data.top_tags ?? [];
  const activity = Object.entries(data.activity_distribution ?? {});
  const location = Object.entries(data.location_distribution ?? {});

  return (
    <div className="card frame-glasses">
      <div className="card-header">
        <div>
          <p className="eyebrow">Vision lifestyle capture</p>
          <div className="card-title">Frame glasses</div>
        </div>
        <Glasses size={18} />
      </div>
      <p className="card-lede">
        Brilliant Labs Frame glasses capture lifestyle photos in the background. Vision analysis
        extracts activity, environment, and habit patterns — all on-device.
      </p>

      <div className="stats-row compact">
        <div className="stat-card"><span><Camera size={12} style={{ verticalAlign: -2, marginRight: 4 }} />Captures</span><strong>{data.captures ?? 0}</strong></div>
        {activity[0] && <div className="stat-card"><span><Activity size={12} style={{ verticalAlign: -2, marginRight: 4 }} />Activity</span><strong>{humanizeTag(activity[0][0])}</strong></div>}
        {location[0] && <div className="stat-card"><span><MapPin size={12} style={{ verticalAlign: -2, marginRight: 4 }} />Location</span><strong>{humanizeTag(location[0][0])}</strong></div>}
      </div>

      {topTags.length > 0 && (
        <div className="chips">
          {topTags.slice(0, 6).map(([tag, count]) => (
            <span key={tag} className="chip chip-muted">{humanizeTag(tag)} · {count}</span>
          ))}
        </div>
      )}

      {data.recommendation && (
        <div className="cs-doctor-note">
          <Lightbulb size={14} style={{ verticalAlign: -2, marginRight: 6 }} />
          <strong>For your doctor: </strong>{data.recommendation}
        </div>
      )}

      <div className="cs-local">
        <Glasses size={13} style={{ verticalAlign: -2, marginRight: 6 }} />
        Vision analysis runs locally. Photos stay on-device; export only on approval.
      </div>
    </div>
  );
}
