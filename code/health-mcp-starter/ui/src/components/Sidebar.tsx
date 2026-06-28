import * as I from "lucide-react";
import { openDemoGuide } from "./DemoGuide";

export type TabId =
  | "dashboard"
  | "capture"
  | "context"
  | "timeline"
  | "condition"
  | "doctor"
  | "datasources"
  | "smart"
  | "sidecar";

type NavItem = { id: TabId; label: string; hint: string; icon: React.ReactNode };
type NavGroup = { title: string; items: NavItem[] };

const GROUPS: NavGroup[] = [
  {
    title: "Overview",
    items: [
      { id: "dashboard", label: "Home", hint: "What matters now", icon: <I.Home size={18} /> }
    ]
  },
  {
    title: "Your health",
    items: [
      { id: "capture", label: "Add data", hint: "Docs & voice notes", icon: <I.Plus size={18} /> },
      { id: "context", label: "My context", hint: "Profile, meds, logs", icon: <I.User size={18} /> },
      { id: "timeline", label: "Timeline", hint: "Day by day", icon: <I.Clock size={18} /> },
      { id: "condition", label: "Condition", hint: "Migraine, sleep, mood", icon: <I.Activity size={18} /> }
    ]
  },
  {
    title: "Analysis",
    items: [
      { id: "smart", label: "Smart view", hint: "Baselines & narrative", icon: <I.Brain size={18} /> },
      { id: "datasources", label: "Data sources", hint: "Omi & Apple", icon: <I.Database size={18} /> }
    ]
  },
  {
    title: "Visit",
    items: [{ id: "doctor", label: "Doctor handoff", hint: "Export & questions", icon: <I.FileText size={18} /> }]
  },
  {
    title: "System",
    items: [
      { id: "sidecar", label: "Sidecar & audit", hint: "Manifest · scopes · audit", icon: <I.ShieldCheck size={18} /> }
    ]
  }
];

type Props = {
  active: TabId;
  onChange: (tab: TabId) => void;
  pendingSuggestions?: number;
  displayName?: string;
};

export function Sidebar({ active, onChange, pendingSuggestions = 0, displayName }: Props) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">VS</div>
        <div>
          <strong>VitaSide</strong>
          <div className="brand-subtitle">
            {displayName ? `for ${displayName}` : "Your patterns, processed locally"}
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {GROUPS.map((group) => (
          <div className="nav-group" key={group.title}>
            <span className="nav-group-title">{group.title}</span>
            {group.items.map((item) => (
              <button
                key={item.id}
                type="button"
                className={active === item.id ? "nav-item active" : "nav-item"}
                onClick={() => onChange(item.id)}
              >
                <span className="icon">{item.icon}</span>
                <div style={{ flex: 1 }}>
                  <div>{item.label}</div>
                  <div className="nav-hint">{item.hint}</div>
                </div>
                {item.id === "context" && pendingSuggestions > 0 && (
                  <span className="badge">{pendingSuggestions}</span>
                )}
              </button>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footnote">
        <button type="button" className="demo-tour-link" onClick={openDemoGuide}>
          <I.MapPin size={13} /> Demo tour — what to look at
        </button>
        <span>Data stays on your Mac · sidecar audit · no cloud by default</span>
      </div>
    </aside>
  );
}
