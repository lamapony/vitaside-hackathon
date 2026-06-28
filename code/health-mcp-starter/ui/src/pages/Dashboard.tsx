import { Briefing, NextStep, Sidecar, UserContext } from "../api";
import { NextStepsPanel } from "../components/NextStepsPanel";
import { WelcomeHero } from "../components/WelcomeHero";
import type { TabId } from "../components/Sidebar";
import { ArrowRight, Lightbulb, User } from "lucide-react";

type Props = {
  briefing?: Briefing;
  sidecar?: Sidecar;
  context?: UserContext;
  nextSteps: NextStep[];
  pendingSuggestions: number;
  onNavigate: (tab: TabId) => void;
};

function profileCompleteness(context?: UserContext) {
  const items = [
    { label: "Profile", done: !!(context?.profile?.display_name) },
    { label: "Goal", done: !!(context?.profile?.main_goal) },
    { label: "Conditions", done: (context?.conditions?.length ?? 0) > 0 },
    { label: "Medications", done: (context?.medications?.length ?? 0) > 0 },
    { label: "Logs", done: (context?.manual_logs?.length ?? 0) > 0 },
  ];
  return { items, filled: items.filter((i) => i.done).length, total: items.length };
}

export function Dashboard({ briefing, sidecar, context, nextSteps, pendingSuggestions, onNavigate }: Props) {
  const insights = briefing?.top_insights ?? [];
  const secondary = insights.slice(1, 3);
  const profile = context?.profile;
  const completeness = profileCompleteness(context);
  const isNewUser = !profile?.display_name && pendingSuggestions > 0;
  const primaryStep = nextSteps[0];

  return (
    <section className="dashboard-page fade-in">
      <WelcomeHero
        briefing={briefing}
        sidecar={sidecar}
        displayName={profile?.display_name}
        nextStep={primaryStep}
        onPrimaryAction={primaryStep ? () => onNavigate(primaryStep.tab as TabId) : undefined}
      />

      {isNewUser && (
        <div className="onboarding-banner">
          <div>
            <strong>Complete your health profile</strong>
            <p>
              We found {pendingSuggestions} suggestions from your notes — confirm your profile and context
              so visit questions and trends reflect your situation.
            </p>
          </div>
          <button type="button" className="primary" onClick={() => onNavigate("context")}>
            Fill in context <ArrowRight size={16} />
          </button>
        </div>
      )}

      <div className="grid grid-2 dashboard-grid">
        <NextStepsPanel steps={nextSteps} onNavigate={onNavigate} />

        <div className="dashboard-side">
          {secondary.length > 0 && (
            <div className="card">
              <div className="card-header">
                <div className="card-title">More observations</div>
                <Lightbulb size={18} />
              </div>
              <div className="insight-grid compact">
                {secondary.map((ins) => (
                  <div key={ins.headline} className="insight-card compact">
                    <div className="insight-headline">{ins.headline}</div>
                    <div className="meta">{ins.detail}</div>
                  </div>
                ))}
              </div>
              <button type="button" className="action-link" onClick={() => onNavigate("smart")}>
                Open pattern analysis <ArrowRight size={14} />
              </button>
            </div>
          )}

          <div className="card">
            <div className="card-header">
              <div className="card-title">Your profile</div>
              <User size={18} />
            </div>
            <div className="progress-row">
              <div className="progress-track">
                <div className="progress-fill" style={{ width: `${Math.round((completeness.filled / completeness.total) * 100)}%` }} />
              </div>
              <div className="progress-value">{completeness.filled}/{completeness.total}</div>
            </div>
            <div className="completeness-checklist">
              {completeness.items.map((it) => (
                <span key={it.label} className={it.done ? "check done" : "check"}>{it.label}</span>
              ))}
            </div>
            <p className="meta profile-hint">
              {profile?.main_goal
                ? `Focus: ${profile.main_goal}`
                : "Add a goal and context — patterns become more useful for your doctor."}
            </p>
            <button type="button" className="secondary compact-btn" onClick={() => onNavigate("context")}>
              {pendingSuggestions > 0 ? `Review ${pendingSuggestions} suggestions` : "Update context"}
            </button>
          </div>

          <div className="card subtle-card">
            <div className="card-header">
              <div className="card-title">Why not ChatGPT?</div>
            </div>
            {briefing?.vs_generic_llm && briefing.vs_generic_llm.length > 0 ? (
              <ul className="vs-llm-list">
                {briefing.vs_generic_llm.map((point, i) => (
                  <li key={i}>{point}</li>
                ))}
              </ul>
            ) : (
              <p className="meta">Every claim cites a dated excerpt from your own notes. Cloud is opt-in only.</p>
            )}
            {briefing?.vs_llm_note && <p className="meta meta-block">{briefing.vs_llm_note}</p>}
          </div>
        </div>
      </div>
    </section>
  );
}
