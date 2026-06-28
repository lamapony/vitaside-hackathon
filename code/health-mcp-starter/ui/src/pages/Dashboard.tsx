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

function calcCompleteness(context?: UserContext, pending?: number) {
  if (!context) return 35;
  let score = 40;
  if (context.profile?.display_name) score += 15;
  if (context.profile?.main_goal) score += 10;
  if ((context.conditions?.length ?? 0) > 0) score += 10;
  if ((context.medications?.length ?? 0) > 0) score += 10;
  score += Math.min((context.manual_logs?.length || 0) * 4, 15);
  score -= (pending || 0) * 4;
  return Math.max(25, Math.min(95, score));
}

export function Dashboard({ briefing, sidecar, context, nextSteps, pendingSuggestions, onNavigate }: Props) {
  const insights = briefing?.top_insights ?? [];
  const secondary = insights.slice(1, 3);
  const profile = context?.profile;
  const completeness = calcCompleteness(context, pendingSuggestions);
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
            <strong>Get started in 2 minutes</strong>
            <p>
              We found {pendingSuggestions} suggestions from your notes — confirm your profile and context
              so recommendations get sharper.
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
                Full analytics <ArrowRight size={14} />
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
                <div className="progress-fill" style={{ width: `${completeness}%` }} />
              </div>
              <div className="progress-value">{completeness}%</div>
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
            <p className="meta">
              <strong>Grounded, not generated.</strong> Every insight links to a dated excerpt from your own notes.
              Cloud is opt-in only.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
