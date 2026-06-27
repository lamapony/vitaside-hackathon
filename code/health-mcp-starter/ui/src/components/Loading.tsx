import { Loader2 } from "lucide-react";

export function Loading({ label = "Загружаем локальные паттерны…" }: { label?: string }) {
  return (
    <div className="loading">
      <Loader2 className="animate-spin" size={20} style={{ marginRight: 8 }} />
      <span>{label}</span>
    </div>
  );
}

export function ErrorBox({ message }: { message: string }) {
  return (
    <div className="error-box" role="alert">
      <strong>Нужна проверка</strong>
      <p>{message}</p>
    </div>
  );
}

export function PartialErrorBanner({ endpoints }: { endpoints: string[] }) {
  if (!endpoints.length) return null;
  return (
    <div className="error-box partial-error" role="status">
      <strong>Часть данных недоступна</strong>
      <p>{endpoints.join(", ")}</p>
    </div>
  );
}
