"""VIT-25: local SQLite longitudinal store + personal baseline windows."""
from __future__ import annotations

import datetime
import json
import os
import sqlite3
import statistics
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sidecar_protocol import audit, check_scope, load_manifest

_SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_WINDOWS = (7, 14, 30)
SCHEMA_VERSION = 1


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def resolve_db_path(manifest: Optional[Dict[str, Any]] = None) -> Path:
    """Pick DB path under manifest scope (fail-closed if explicit path escapes scope)."""
    manifest = manifest or load_manifest()
    env_path = os.getenv("VITASIDE_LONGITUDINAL_DB")
    if env_path:
        db_path = Path(os.path.expanduser(env_path)).resolve()
    else:
        from sidecar_protocol import allowed_roots

        roots = allowed_roots(manifest)
        if roots:
            db_path = (roots[0] / ".vitaside" / "longitudinal.db").resolve()
        else:
            db_path = (_SCRIPT_DIR / "demo-data" / "vault" / "050 Daily Omi" / ".vitaside" / "longitudinal.db").resolve()

    roots = []
    from sidecar_protocol import allowed_roots as _roots

    roots = _roots(manifest)
    if roots and not check_scope(manifest, db_path):
        audit("longitudinal_db_denied", {"path": str(db_path)})
        raise RuntimeError(f"Longitudinal DB path is outside manifest scope: {db_path}")
    return db_path


def connect(db_path: Optional[Path] = None, manifest: Optional[Dict[str, Any]] = None) -> sqlite3.Connection:
    manifest = manifest or load_manifest()
    path = db_path or resolve_db_path(manifest)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    migrate(conn)
    return conn


def migrate(conn: sqlite3.Connection) -> int:
    """Idempotent schema migration. Safe to call multiple times."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_metric (
            day TEXT NOT NULL,
            metric_key TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT,
            source TEXT NOT NULL DEFAULT 'derived',
            updated_at TEXT NOT NULL,
            PRIMARY KEY (day, metric_key, source)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_signal (
            day TEXT NOT NULL,
            signal TEXT NOT NULL,
            quality REAL,
            source TEXT NOT NULL DEFAULT 'omi',
            updated_at TEXT NOT NULL,
            PRIMARY KEY (day, signal, source)
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_metric_key ON daily_metric(metric_key, day)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_signal_key ON daily_signal(signal, day)")

    row = conn.execute("SELECT MAX(version) AS v FROM schema_migrations").fetchone()
    current = int(row["v"] or 0)
    if current < SCHEMA_VERSION:
        conn.execute(
            "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES (?, ?)",
            (SCHEMA_VERSION, _utc_now()),
        )
        conn.commit()
    return SCHEMA_VERSION


def _metric_rows_from_entries(entries: Iterable[Dict[str, Any]]) -> List[Tuple[str, str, float, Optional[str], str]]:
    rows: List[Tuple[str, str, float, Optional[str], str]] = []
    now = _utc_now()
    for entry in entries:
        day = entry.get("date")
        if not day:
            continue
        journal = entry.get("journal_id", "omi")
        for sig in entry.get("signals", []):
            rows.append((day, f"signal:{sig}", 1.0, "presence", journal))
        sq = entry.get("sleep_quality")
        if sq in ("good", "poor"):
            rows.append((day, "sleep_quality_score", 1.0 if sq == "good" else 0.0, "ordinal", journal))
        for swq in entry.get("signals_with_quality", []):
            sig = swq.get("signal")
            q = swq.get("quality_score")
            if sig and isinstance(q, (int, float)):
                rows.append((day, f"signal_quality:{sig}", float(q), "score", journal))
    return rows


def sync_entries(
    conn: sqlite3.Connection,
    entries: Sequence[Dict[str, Any]],
    *,
    source: str = "omi",
) -> Dict[str, int]:
    """Upsert daily signals/metrics from journal entries."""
    now = _utc_now()
    signal_rows = 0
    metric_rows = 0
    for entry in entries:
        day = entry.get("date")
        if not day:
            continue
        for sig in entry.get("signals", []):
            conn.execute(
                """
                INSERT INTO daily_signal(day, signal, quality, source, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(day, signal, source) DO UPDATE SET
                    quality=excluded.quality,
                    updated_at=excluded.updated_at
                """,
                (day, sig, None, source, now),
            )
            signal_rows += 1
        for swq in entry.get("signals_with_quality", []):
            sig = swq.get("signal")
            q = swq.get("quality_score")
            if sig:
                conn.execute(
                    """
                    INSERT INTO daily_signal(day, signal, quality, source, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(day, signal, source) DO UPDATE SET
                        quality=excluded.quality,
                        updated_at=excluded.updated_at
                    """,
                    (day, sig, float(q) if isinstance(q, (int, float)) else None, source, now),
                )

    for day, key, value, unit, src in _metric_rows_from_entries(entries):
        conn.execute(
            """
            INSERT INTO daily_metric(day, metric_key, value, unit, source, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(day, metric_key, source) DO UPDATE SET
                value=excluded.value,
                unit=excluded.unit,
                updated_at=excluded.updated_at
            """,
            (day, key, value, unit, src, now),
        )
        metric_rows += 1
    conn.commit()
    return {"signals_upserted": signal_rows, "metrics_upserted": metric_rows}


def load_fixture_rows(fixture_path: Path) -> List[Dict[str, Any]]:
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    return data.get("metrics", [])


def sync_fixture_metrics(conn: sqlite3.Connection, metrics: Sequence[Dict[str, Any]]) -> int:
    now = _utc_now()
    count = 0
    for row in metrics:
        day = row["day"]
        key = row["metric_key"]
        value = float(row["value"])
        unit = row.get("unit")
        source = row.get("source", "fixture")
        conn.execute(
            """
            INSERT INTO daily_metric(day, metric_key, value, unit, source, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(day, metric_key, source) DO UPDATE SET
                value=excluded.value,
                unit=excluded.unit,
                updated_at=excluded.updated_at
            """,
            (day, key, value, unit, source, now),
        )
        count += 1
    conn.commit()
    return count


def _dates_for_metric(conn: sqlite3.Connection, metric_key: str) -> List[str]:
    rows = conn.execute(
        "SELECT DISTINCT day FROM daily_metric WHERE metric_key = ? ORDER BY day",
        (metric_key,),
    ).fetchall()
    return [r["day"] for r in rows]


def _values_in_window(conn: sqlite3.Connection, metric_key: str, end_day: str, window: int) -> List[float]:
    rows = conn.execute(
        """
        SELECT day, value FROM daily_metric
        WHERE metric_key = ? AND day <= ?
        ORDER BY day DESC
        LIMIT ?
        """,
        (metric_key, end_day, window),
    ).fetchall()
    if not rows:
        return []
    return [float(r["value"]) for r in reversed(rows)]


def _signal_presence_window(
    conn: sqlite3.Connection, signal: str, end_day: str, window: int
) -> Tuple[List[str], float]:
    rows = conn.execute(
        """
        SELECT DISTINCT day FROM daily_signal
        WHERE signal = ? AND day <= ?
        ORDER BY day DESC
        LIMIT ?
        """,
        (signal, end_day, window),
    ).fetchall()
    days = [r["day"] for r in reversed(rows)]
    if not days:
        return [], 0.0
    # frequency = days with signal / window length (calendar span)
    span_start = datetime.date.fromisoformat(days[0])
    span_end = datetime.date.fromisoformat(end_day)
    span = max((span_end - span_start).days + 1, 1)
    return days, len(days) / span


def _trend_label(recent: float, prior: float) -> str:
    if prior <= 0 and recent <= 0:
        return "stable"
    if prior <= 0:
        return "rising" if recent > 0 else "stable"
    ratio = recent / prior
    if ratio > 1.15:
        return "rising"
    if ratio < 0.85:
        return "falling"
    return "stable"


def _window_stats(values: List[float]) -> Dict[str, Any]:
    if not values:
        return {"mean": None, "std": None, "n": 0, "trend": "insufficient_data"}
    mean_v = statistics.mean(values)
    std_v = statistics.stdev(values) if len(values) > 1 else 0.0
    mid = len(values) // 2 or 1
    recent = statistics.mean(values[mid:]) if len(values) > 1 else mean_v
    prior = statistics.mean(values[:mid]) if len(values) > 1 else mean_v
    return {
        "mean": round(mean_v, 4),
        "std": round(std_v, 4),
        "n": len(values),
        "trend": _trend_label(recent, prior),
    }


def compute_personal_baselines(
    conn: sqlite3.Connection,
    *,
    metric_keys: Optional[Sequence[str]] = None,
    windows: Sequence[int] = DEFAULT_WINDOWS,
    end_day: Optional[str] = None,
) -> Dict[str, Any]:
    """Return baseline JSON for metrics and signals across 7/14/30d windows."""
    end_row = conn.execute("SELECT MAX(day) AS d FROM daily_metric").fetchone()
    signal_end = conn.execute("SELECT MAX(day) AS d FROM daily_signal").fetchone()
    candidates = [d for d in (end_row["d"] if end_row else None, signal_end["d"] if signal_end else None) if d]
    if not candidates:
        return {"end_day": None, "windows": list(windows), "metrics": {}, "signals": {}, "citations": []}
    resolved_end_day: str = end_day or max(candidates)

    if metric_keys:
        keys = list(metric_keys)
    else:
        key_rows = conn.execute("SELECT DISTINCT metric_key FROM daily_metric ORDER BY metric_key").fetchall()
        keys = [r["metric_key"] for r in key_rows]

    metrics_out: Dict[str, Dict[str, Any]] = {}
    for key in keys:
        per_window = {}
        for w in windows:
            vals = _values_in_window(conn, key, resolved_end_day, w)
            per_window[str(w)] = _window_stats(vals)
        metrics_out[key] = per_window

    signal_rows = conn.execute("SELECT DISTINCT signal FROM daily_signal ORDER BY signal").fetchall()
    signals_out: Dict[str, Dict[str, Any]] = {}
    for row in signal_rows:
        sig = row["signal"]
        per_window = {}
        for w in windows:
            days, freq = _signal_presence_window(conn, sig, resolved_end_day, w)
            per_window[str(w)] = {
                "presence_freq": round(freq, 4),
                "days_with_signal": len(days),
                "n": w,
                "trend": "insufficient_data" if not days else "stable",
            }
        signals_out[sig] = per_window

    citations = [
        {
            "date": resolved_end_day,
            "source": "sqlite_longitudinal",
            "excerpt": "Baseline computed from local longitudinal store (metadata only).",
        }
    ]
    return {
        "end_day": resolved_end_day,
        "windows": list(windows),
        "metrics": metrics_out,
        "signals": signals_out,
        "citations": citations,
    }


def get_personal_baselines_payload(
    entries: Sequence[Dict[str, Any]],
    *,
    manifest: Optional[Dict[str, Any]] = None,
    metric_keys: Optional[Sequence[str]] = None,
    windows: Sequence[int] = DEFAULT_WINDOWS,
    fixture_path: Optional[Path] = None,
) -> Dict[str, Any]:
    manifest = manifest or load_manifest()
    db_path = resolve_db_path(manifest)
    conn = connect(db_path, manifest)
    sync_entries(conn, entries)
    if fixture_path and fixture_path.exists():
        sync_fixture_metrics(conn, load_fixture_rows(fixture_path))
    baselines = compute_personal_baselines(conn, metric_keys=metric_keys, windows=windows)
    conn.close()
    baselines["db_path"] = str(db_path)
    baselines["storage"] = "sqlite_local"
    return baselines