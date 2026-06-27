import * as I from "lucide-react";

export type TabId =
  | "dashboard"
  | "context"
  | "timeline"
  | "condition"
  | "doctor"
  | "datasources"
  | "smart";

type NavItem = { id: TabId; label: string; hint: string; icon: React.ReactNode };
type NavGroup = { title: string; items: NavItem[] };

const GROUPS: NavGroup[] = [
  {
    title: "Обзор",
    items: [
      { id: "dashboard", label: "Главная", hint: "Что важно сейчас", icon: <I.Home size={18} /> }
    ]
  },
  {
    title: "Ваше здоровье",
    items: [
      { id: "context", label: "Мой контекст", hint: "Профиль, лекарства", icon: <I.User size={18} /> },
      { id: "timeline", label: "Хронология", hint: "День за днём", icon: <I.Clock size={18} /> },
      { id: "condition", label: "Состояние", hint: "Мигрень, биполярка…", icon: <I.Activity size={18} /> }
    ]
  },
  {
    title: "Анализ",
    items: [
      { id: "smart", label: "Умный обзор", hint: "Базовые линии", icon: <I.Brain size={18} /> },
      { id: "datasources", label: "Источники", hint: "Omi и Apple", icon: <I.Database size={18} /> }
    ]
  },
  {
    title: "Визит",
    items: [{ id: "doctor", label: "К врачу", hint: "Экспорт и вопросы", icon: <I.FileText size={18} /> }]
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
            {displayName ? `для ${displayName}` : "ваши паттерны — локально"}
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
        Данные на вашем Mac · аудит sidecar · без облака по умолчанию
      </div>
    </aside>
  );
}
