import { Briefing, NextStep, Sidecar } from "../api";
import { Shield, Sparkles, Database } from "lucide-react";

type Props = {
  briefing?: Briefing;
  sidecar?: Sidecar;
  displayName?: string;
  nextStep?: NextStep;
  onPrimaryAction?: () => void;
};

function greeting(name?: string) {
  const h = new Date().getHours();
  const part = h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening";
  return name ? `${part}, ${name}` : part;
}

export function WelcomeHero({ briefing, sidecar, displayName, nextStep, onPrimaryAction }: Props) {
  const footprint = briefing?.data_footprint;
  const days = footprint?.days_analyzed ?? briefing?.days_analyzed ?? 0;
  const isDemo = footprint?.data_mode === "demo";
  const oneLiner = briefing?.one_liner ?? briefing?.top_insights?.[0]?.headline;
  const top = briefing?.top_insights?.[0];

  return (
    <div className="welcome-hero">
      <div className="welcome-hero-inner">
        <p className="welcome-greeting">{greeting(displayName)}</p>
        <h1 className="welcome-headline">
          {oneLiner ?? "Your health patterns — from your notes, not the internet"}
        </h1>
        <p className="welcome-sub">
          VitaSide reads local notes and wearables, finds patterns over time, and helps you prepare for visits.
          Not a diagnosis — a personal, citation-backed overview.
        </p>

        <div className="welcome-stats">
          <div className="welcome-stat">
            <strong>{days || "—"}</strong>
            <span>days tracked</span>
          </div>
          <div className="welcome-stat">
            <strong>{briefing?.top_insights?.length ?? 0}</strong>
            <span>observations</span>
          </div>
          <div className="welcome-stat">
            <strong>{footprint?.overlap_days ?? 0}</strong>
            <span>Omi + Apple</span>
          </div>
          {isDemo && (
            <div className="welcome-stat demo">
              <strong>Demo</strong>
              <span>sample vault</span>
            </div>
          )}
        </div>

        <div className="welcome-trust">
          <span><Shield size={14} /> Local-first</span>
          <span><Sparkles size={14} /> Citation-backed</span>
          <span><Database size={14} /> {sidecar?.name ?? "Sidecar"} active</span>
        </div>

        {nextStep && onPrimaryAction && (
          <button type="button" className="welcome-cta primary" onClick={onPrimaryAction}>
            {nextStep.action_label || nextStep.title}
          </button>
        )}
      </div>

      {top?.evidence_quote && (
        <aside className="welcome-proof">
          <p className="eyebrow">From your notes</p>
          <blockquote>{top.evidence_quote}</blockquote>
          {top.evidence_date && <p className="meta">{top.evidence_date}</p>}
        </aside>
      )}
    </div>
  );
}
