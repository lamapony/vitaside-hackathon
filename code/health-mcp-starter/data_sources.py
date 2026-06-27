"""
Data sources catalog + analysis mechanics for VitaSide.

Single place to answer: «откуда берётся информация для анализа» и
«какие шаги её обрабатывают».
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# ---------------------------------------------------------------------------
# Catalog — what CAN be used (static registry)
# ---------------------------------------------------------------------------

SOURCE_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "omi_vault",
        "type": "local_files",
        "label": "Omi daily conversations (Obsidian vault)",
        "label_ru": "Ежедневные разговоры Omi (Obsidian vault)",
        "description": "Markdown notes from Omi voice assistant — primary signal source.",
        "description_ru": "Markdown-заметки из Omi — основной источник сигналов (сон, стресс, настроение).",
        "env_vars": [
            {"name": "OMI_VAULT_PATH", "required": True, "example": "~/Documents/Obsidian Vault"},
            {"name": "VITASIDE_OMI_PATHS", "required": False, "example": "/path/a:/path/b", "note": "Extra search roots, colon-separated"},
        ],
        "discovery": {
            "relative_paths": [
                "050 Daily Omi/Conversations",
                "050 Daily Omi",
                "Daily Notes",
                "Journal",
                "Health",
            ],
            "file_glob": "**/*.md",
        },
        "provides": [
            "signals (sleep, stress, mood_low, mood_good, exercise, …)",
            "dated excerpts / citations",
            "sleep_quality (good/poor/unknown)",
            "time_of_day, speaker separation",
            "context words (сегодня/вчера)",
        ],
        "consumed_by": [
            "analyze_lifestyle_patterns",
            "smart_analysis",
            "get_actionable_briefing",
            "simulate_whatif",
            "generate_doctor_report",
            "track_condition",
        ],
        "setup_steps": [
            "Install Omi → enable Obsidian export to your vault",
            "export OMI_VAULT_PATH=/path/to/Obsidian\\ Vault",
            "Notes should land under 050 Daily Omi/Conversations/YYYY/MM/",
        ],
        "setup_steps_ru": [
            "Omi → экспорт в Obsidian vault",
            "export OMI_VAULT_PATH=/путь/к/vault",
            "Файлы: 050 Daily Omi/Conversations/ГГГГ/ММ/ГГГГ-ММ-ДД.md",
        ],
        "privacy": "local_only",
    },
    {
        "id": "apple_health",
        "type": "local_export",
        "label": "Apple Health export.xml",
        "label_ru": "Экспорт Apple Health (export.xml)",
        "description": "Objective wearable metrics merged by date with Omi notes.",
        "description_ru": "Объективные метрики с часов/телефона — merge с Omi по дате.",
        "env_vars": [],
        "discovery": {
            "search_paths": [
                "{vault}/Apple Health/export.xml",
                "~/Downloads/apple_health_export/export.xml",
                "~/Documents/apple_health_export/export.xml",
                "~/Desktop/apple_health_export/export.xml",
            ],
        },
        "provides": [
            "sleep_hours (daily)",
            "heart_rate_avg",
            "hrv_sdnn",
            "steps",
            "wearable personal bands",
            "omi↔apple alignment insights",
        ],
        "consumed_by": [
            "combine_omi_and_apple",
            "smart_analysis (wearable_bands)",
            "generate_doctor_report",
            "get_actionable_briefing (merge insights)",
        ],
        "setup_steps": [
            "iPhone: Health app → Profile → Export All Health Data",
            "Unzip to ~/Downloads/apple_health_export/",
            "Re-run analysis — auto-detected, no env var needed",
        ],
        "setup_steps_ru": [
            "iPhone: Здоровье → Профиль → Экспорт всех данных",
            "Распаковать в ~/Downloads/apple_health_export/",
            "Перезапустить анализ — путь подхватится автоматически",
        ],
        "privacy": "local_only",
        "fallback": "demo_daily synthetic series when export missing",
    },
    {
        "id": "sidecar_manifest",
        "type": "protocol",
        "label": "Sidecar manifest (scopes + TTL)",
        "label_ru": "Манифест sidecar (scopes + TTL)",
        "description": "YAML manifest defines which paths the sidecar may read and when it expires.",
        "description_ru": "YAML-манифест: какие пути можно читать и срок действия sidecar.",
        "env_vars": [
            {"name": "VITASIDE_MANIFEST", "required": False, "example": "sidecars/sleep-stress-sidecar/manifest.yaml"},
        ],
        "discovery": {"default": "sidecars/sleep-stress-sidecar/manifest.yaml"},
        "provides": [
            "allowed_scopes (path ACL)",
            "tool whitelist",
            "TTL / expiry",
            "quality_gates",
            "condition_pack binding",
            "azure allowed_operations",
        ],
        "consumed_by": ["_scan_omi (scope check)", "get_sidecar_status", "audit.log"],
        "setup_steps": ["./issue-sidecar.sh sleep-stress-sidecar", "export VITASIDE_MANIFEST=.../manifest.yaml"],
        "setup_steps_ru": ["./issue-sidecar.sh sleep-stress-sidecar", "export VITASIDE_MANIFEST=.../manifest.yaml"],
        "privacy": "local_only",
    },
    {
        "id": "manual_log",
        "type": "local_json",
        "label": "Quick manual logs (dashboard)",
        "label_ru": "Быстрые записи (дашборд)",
        "description": "Headache scores, meds, one-liners — stored in local-data/user_context.json",
        "description_ru": "Оценка боли, лекарства, заметки — local-data/user_context.json",
        "env_vars": [],
        "discovery": {"path": "local-data/user_context.json", "field": "manual_logs"},
        "provides": ["typed quick logs", "severity", "merges into combined timeline"],
        "consumed_by": ["list_journals", "headache_insights", "journal_summary", "merge_entries"],
        "setup_steps": ["Dashboard → My context → Quick log", "Or POST /api/manual-logs"],
        "setup_steps_ru": ["Дашборд → My context → быстрая запись", "Или POST /api/manual-logs"],
        "privacy": "local_only",
    },
    {
        "id": "host_context",
        "type": "agent_input",
        "label": "Main agent life context (Hermes)",
        "label_ru": "Контекст главного агента (Hermes)",
        "description": "Calendar-like events passed by host agent for collaborative_insight.",
        "description_ru": "События (travel, deadline) от главного агента для collaborative_insight.",
        "env_vars": [],
        "discovery": {"source": "MCP tool argument host_context or DEFAULT_HOST_CONTEXT demo"},
        "provides": ["travel dates", "deadline windows", "event notes"],
        "consumed_by": ["collaborative_insight"],
        "setup_steps": [
            "Hermes passes host_context.events[] when calling collaborative_insight",
            "Demo uses built-in DEFAULT_HOST_CONTEXT",
        ],
        "setup_steps_ru": [
            "Hermes передаёт host_context.events[] в collaborative_insight",
            "В демо — встроенный DEFAULT_HOST_CONTEXT",
        ],
        "privacy": "local_only",
    },
    {
        "id": "condition_packs",
        "type": "local_yaml",
        "label": "Condition tracking packs",
        "label_ru": "Пакеты condition tracking",
        "description": "YAML packs for migraine, bipolar — extra signals and doctor focus.",
        "description_ru": "YAML-паки migraine/bipolar — доп. сигналы и фокус для врача.",
        "env_vars": [
            {"name": "VITASIDE_CONDITION_PACK", "required": False, "example": "migraine"},
        ],
        "discovery": {"directory": "condition_packs/", "files": "*.yaml"},
        "provides": ["track_items", "metrics", "doctor_focus bullets", "pack-specific signals"],
        "consumed_by": ["track_condition", "condition_report", "generate_visit_questions"],
        "setup_steps": [
            "./issue-sidecar.sh migraine-tracking-sidecar",
            "or export VITASIDE_CONDITION_PACK=migraine",
        ],
        "setup_steps_ru": [
            "./issue-sidecar.sh migraine-tracking-sidecar",
            "или export VITASIDE_CONDITION_PACK=migraine",
        ],
        "privacy": "local_only",
    },
    {
        "id": "audit_log",
        "type": "local_file",
        "label": "Audit log",
        "label_ru": "Audit log",
        "description": "Append-only log of every tool access and files read.",
        "description_ru": "Append-only лог каждого доступа к данным.",
        "env_vars": [{"name": "VITASIDE_AUDIT_LOG", "required": False, "example": "./audit.log"}],
        "discovery": {"default": "audit.log"},
        "provides": ["access trail", "files_read per tool", "timestamps"],
        "consumed_by": ["get_sidecar_status", "generate_doctor_report", "export_visit_bundle"],
        "setup_steps": ["Automatic — written on every scoped read"],
        "setup_steps_ru": ["Автоматически — пишется при каждом scoped read"],
        "privacy": "local_only",
    },
    {
        "id": "azure_boost",
        "type": "optional_cloud",
        "label": "Azure OpenAI / share (optional, consent)",
        "label_ru": "Azure OpenAI / share (опционально, с consent)",
        "description": "Enrichment narrative or time-limited doctor link — minimized payload only.",
        "description_ru": "Обогащение narrative или ссылка врачу — только минимизированный payload.",
        "env_vars": [
            {"name": "VITASIDE_AZURE_MODE", "required": False, "example": "stub|live"},
            {"name": "AZURE_OPENAI_ENDPOINT", "required": False},
            {"name": "AZURE_OPENAI_DEPLOYMENT", "required": False},
            {"name": "AZURE_OPENAI_API_KEY", "required": False},
            {"name": "AZURE_FUNCTION_SHARE_URL", "required": False},
        ],
        "discovery": {"manifest_flag": "enable_azure_boost", "sidecar": "azure-hybrid-sidecar"},
        "provides": ["narrative enrichment", "share_url (TTL)"],
        "consumed_by": ["azure_enhance_insight", "azure_share_report"],
        "setup_steps": [
            "./issue-sidecar.sh azure-hybrid-sidecar",
            "preview_azure_payload → user_consent=True → azure_enhance_insight",
        ],
        "setup_steps_ru": [
            "./issue-sidecar.sh azure-hybrid-sidecar",
            "preview_azure_payload → user_consent=True → azure_enhance_insight",
        ],
        "privacy": "opt_in_cloud",
        "fallback": "local_narrative_engine (no network)",
    },
]

ANALYSIS_PIPELINE: List[Dict[str, Any]] = [
    {
        "step": 1,
        "id": "resolve_vault",
        "name": "Resolve data vault",
        "name_ru": "Выбор vault",
        "inputs": ["omi_vault"],
        "outputs": ["vault_path", "data_mode: explicit|auto|demo"],
        "mechanic": "OMI_VAULT_PATH if set; else auto-detect real vault (≥3 parseable files); else demo-data/vault",
        "code": "_resolve_vault",
    },
    {
        "step": 2,
        "id": "scope_enforce",
        "name": "Sidecar scope check",
        "name_ru": "Проверка scope sidecar",
        "inputs": ["sidecar_manifest", "omi_vault"],
        "outputs": ["allowed_files[]"],
        "mechanic": "Each .md must be under manifest allowed_scopes; denied paths never read",
        "code": "check_scope + assert_sidecar_active",
    },
    {
        "step": 3,
        "id": "parse_omi",
        "name": "Parse Omi markdown",
        "name_ru": "Парсинг Omi markdown",
        "inputs": ["omi_vault"],
        "outputs": ["entries[]", "signals[]", "excerpts", "sleep_quality", "quality_score"],
        "mechanic": "Regex signal patterns + speaker lines + context words + audit log entry",
        "code": "_parse_omi_file → _scan_omi",
    },
    {
        "step": 4,
        "id": "timeseries",
        "name": "Build daily timeseries",
        "name_ru": "Дневной timeseries",
        "inputs": ["entries"],
        "outputs": ["by_date", "signal_series"],
        "mechanic": "One row per calendar date; signals union per day",
        "code": "_build_timeseries",
    },
    {
        "step": 5,
        "id": "correlations",
        "name": "Temporal correlations (lag 1–3d)",
        "name_ru": "Временные корреляции (lag 1–3 дня)",
        "inputs": ["timeseries"],
        "outputs": ["temporal_correlations", "citations", "p_values"],
        "mechanic": "Cause day → effect day+lag; rank by lift; enrich with excerpts; scipy binomial p-value",
        "code": "_compute_temporal_correlations + add_pvalues + _enrich_correlations",
    },
    {
        "step": 6,
        "id": "smart_layer",
        "name": "Personal intelligence",
        "name_ru": "Персональный intelligence-слой",
        "inputs": ["entries", "correlations", "apple_health"],
        "outputs": ["personal_baselines", "weekday_effects", "attention_now", "wearable_bands"],
        "mechanic": "Rolling 28d bands, weekday histograms, anomalies vs YOUR history — not population norms",
        "code": "smart_analytics.run_smart_analysis",
    },
    {
        "step": 7,
        "id": "apple_merge",
        "name": "Omi ↔ Apple daily merge",
        "name_ru": "Merge Omi ↔ Apple по дате",
        "inputs": ["entries", "apple_health"],
        "outputs": ["merged_insights", "overlap_days"],
        "mechanic": "Match subjective sleep_quality vs sleep_hours; stress vs low HRV same day",
        "code": "apple_merge.merge_with_omi",
    },
    {
        "step": 8,
        "id": "whatif",
        "name": "What-if simulation",
        "name_ru": "What-if симуляция",
        "inputs": ["entries"],
        "outputs": ["projected_outcomes", "confidence"],
        "mechanic": "Compare day-after signal rates following good vs poor sleep nights in YOUR history",
        "code": "_simulate_whatif_core",
    },
    {
        "step": 9,
        "id": "briefing",
        "name": "Actionable briefing",
        "name_ru": "Actionable briefing",
        "inputs": ["correlations", "apple_merge", "whatif", "smart_layer", "period_compare"],
        "outputs": ["top_insights[]", "evidence_date", "evidence_quote", "why_not_llm"],
        "mechanic": "Every insight MUST cite date+excerpt or computed stat — no generic advice",
        "code": "actionable_insights.build_actionable_briefing",
    },
    {
        "step": 10,
        "id": "narrative",
        "name": "Local narrative (optional Azure)",
        "name_ru": "Локальный narrative (опц. Azure)",
        "inputs": ["briefing", "smart_layer"],
        "outputs": ["narrative", "evidence_map"],
        "mechanic": "Cite-grounded prose; Azure only sends minimized aggregates with consent",
        "code": "narrative_engine.build_local_narrative / azure_boost",
    },
    {
        "step": 11,
        "id": "export",
        "name": "Doctor handoff export",
        "name_ru": "Экспорт для врача",
        "inputs": ["briefing", "analysis", "whatif", "visit_questions"],
        "outputs": ["vitaside-report-*.html", "vitaside-doctor-*.html", "visit-prep-*.md"],
        "mechanic": "Static HTML + Obsidian note; audit.log proves files read",
        "code": "generate_doctor_report + export_visit_bundle",
    },
]

TOOL_RESOURCE_MAP: Dict[str, List[str]] = {
    "analyze_lifestyle_patterns": ["omi_vault", "sidecar_manifest", "apple_health", "audit_log"],
    "smart_analysis": ["omi_vault", "apple_health", "sidecar_manifest"],
    "get_actionable_briefing": ["omi_vault", "apple_health", "sidecar_manifest"],
    "simulate_whatif": ["omi_vault", "sidecar_manifest"],
    "combine_omi_and_apple": ["omi_vault", "apple_health", "sidecar_manifest"],
    "collaborative_insight": ["omi_vault", "host_context", "apple_health", "sidecar_manifest"],
    "track_condition": ["omi_vault", "condition_packs", "sidecar_manifest"],
    "generate_doctor_report": ["omi_vault", "apple_health", "sidecar_manifest", "audit_log"],
    "generate_visit_questions": ["omi_vault", "apple_health", "sidecar_manifest"],
    "azure_enhance_insight": ["omi_vault", "apple_health", "azure_boost", "sidecar_manifest"],
    "list_journals": ["omi_vault", "manual_log", "sidecar_manifest"],
    "headache_insights": ["omi_vault", "manual_log", "sidecar_manifest", "condition_packs"],
    "journal_summary": ["omi_vault", "manual_log"],
    "list_data_sources": ["sidecar_manifest", "manual_log"],
}


def omi_search_paths(vault: Path) -> List[Path]:
    paths: List[Path] = []
    for part in os.getenv("VITASIDE_OMI_PATHS", "").split(":"):
        if part.strip():
            p = Path(part.strip()).expanduser()
            if p.exists():
                paths.append(p)
    for rel in ("050 Daily Omi/Conversations", "050 Daily Omi", "Daily Notes", "Journal", "Health"):
        p = vault / rel
        if p.exists() and p not in paths:
            paths.append(p)
    return paths or [vault]


def apple_search_paths(vault: Path) -> List[Path]:
    return [
        vault / "Apple Health",
        Path.home() / "Downloads" / "apple_health_export",
        Path.home() / "Documents" / "apple_health_export",
        Path.home() / "Desktop" / "apple_health_export",
    ]


def find_apple_export(vault: Path) -> Optional[Path]:
    for base in apple_search_paths(vault):
        xml = base / "export.xml"
        if xml.exists():
            return xml
    return None


def _count_omi_files(vault: Path) -> Dict[str, Any]:
    paths = omi_search_paths(vault)
    files: List[Path] = []
    for base in paths:
        files.extend(base.rglob("*.md"))
    by_folder: Dict[str, int] = {}
    for f in files:
        try:
            rel = str(f.parent.relative_to(vault))
        except ValueError:
            rel = str(f.parent)
        by_folder[rel] = by_folder.get(rel, 0) + 1
    return {
        "total_md_files": len(files),
        "search_roots": [str(p) for p in paths],
        "by_folder": dict(sorted(by_folder.items(), key=lambda x: -x[1])[:12]),
    }


def _source_status(source_id: str, vault: Path, manifest: Dict[str, Any], apple_xml: Optional[Path], **extra) -> Dict[str, Any]:
    """Live resolution status for one catalog entry."""
    base = next(s for s in SOURCE_CATALOG if s["id"] == source_id)
    row: Dict[str, Any] = {
        "id": source_id,
        "label": base["label"],
        "label_ru": base["label_ru"],
        "type": base["type"],
        "privacy": base["privacy"],
        "provides": base["provides"],
        "consumed_by": base["consumed_by"],
        "setup_steps": base.get("setup_steps", []),
        "setup_steps_ru": base.get("setup_steps_ru", []),
    }

    if source_id == "omi_vault":
        omi = _count_omi_files(vault)
        scoped = extra.get("scoped_parseable")
        if extra.get("data_mode") == "explicit" and omi["total_md_files"] == 0:
            row["status"] = "explicit_empty"
        elif extra.get("data_mode") == "explicit" and omi["total_md_files"] > 0 and scoped == 0:
            row["status"] = "scope_blocked"
        elif omi["total_md_files"] >= 3:
            row["status"] = "connected"
        elif extra.get("data_mode") == "demo":
            row["status"] = "demo"
        else:
            row["status"] = "sparse"
        row["resolved_path"] = str(vault)
        row["env"] = {"OMI_VAULT_PATH": os.getenv("OMI_VAULT_PATH", "")}
        row["stats"] = {**omi, **({"scoped_parseable": scoped} if scoped is not None else {})}
    elif source_id == "apple_health":
        if apple_xml:
            size_mb = round(apple_xml.stat().st_size / (1024 * 1024), 2)
            row["status"] = "connected"
            row["resolved_path"] = str(apple_xml)
            row["stats"] = {"export_size_mb": size_mb, "mode": "real"}
        else:
            row["status"] = "demo_fallback"
            row["resolved_path"] = None
            row["stats"] = {"mode": "demo_daily", "note": "Synthetic Apple series — export Health data for real metrics"}
            row["candidates_checked"] = [str(p / "export.xml") for p in apple_search_paths(vault)]
    elif source_id == "sidecar_manifest":
        row["status"] = "active" if manifest.get("_loaded") else "default"
        row["resolved_path"] = manifest.get("_manifest_path")
        row["stats"] = {
            "name": manifest.get("name"),
            "expires_at": manifest.get("_expires_at"),
            "scopes": len(manifest.get("allowed_scopes", [])),
            "tools": len(manifest.get("tools", [])),
        }
    elif source_id == "host_context":
        row["status"] = "available"
        row["stats"] = {"demo_events": extra.get("host_events", 0)}
    elif source_id == "condition_packs":
        packs_dir = extra.get("packs_dir") or Path(__file__).parent / "condition_packs"
        pack_files = list(packs_dir.glob("*.yaml")) if packs_dir.exists() else []
        active = extra.get("active_condition")
        row["status"] = "connected" if pack_files else "missing"
        row["resolved_path"] = str(packs_dir)
        row["stats"] = {"pack_count": len(pack_files), "pack_ids": [f.stem for f in pack_files], "active": active}
    elif source_id == "audit_log":
        log_path = Path(os.getenv("VITASIDE_AUDIT_LOG", Path(__file__).parent / "audit.log"))
        row["status"] = "connected" if log_path.exists() else "empty"
        row["resolved_path"] = str(log_path)
        row["stats"] = {"size_bytes": log_path.stat().st_size if log_path.exists() else 0}
    elif source_id == "azure_boost":
        enabled = extra.get("azure_enabled", False)
        row["status"] = "enabled" if enabled else "disabled"
        row["stats"] = {
            "mode": os.getenv("VITASIDE_AZURE_MODE", "stub"),
            "live_openai": bool(os.getenv("AZURE_OPENAI_ENDPOINT")),
        }
    else:
        row["status"] = "unknown"

    return row


def build_sources_snapshot(
    vault: Path,
    manifest: Dict[str, Any],
    *,
    data_mode: str = "auto",
    active_condition: Optional[str] = None,
    azure_enabled_flag: bool = False,
    host_events: int = 0,
    parseable_count: Optional[int] = None,
    scoped_parseable: Optional[int] = None,
) -> Dict[str, Any]:
    """Full catalog + live status for MCP / API / UI."""
    apple_xml = find_apple_export(vault)
    sources = [
        _source_status(
            s["id"],
            vault,
            manifest,
            apple_xml,
            data_mode=data_mode,
            active_condition=active_condition,
            azure_enabled=azure_enabled_flag,
            host_events=host_events,
            packs_dir=Path(__file__).parent / "condition_packs",
            scoped_parseable=scoped_parseable if s["id"] == "omi_vault" else None,
        )
        for s in SOURCE_CATALOG
    ]

    connected = [s["id"] for s in sources if s["status"] in ("connected", "active", "enabled", "available", "demo")]
    missing = [s["id"] for s in sources if s["status"] in (
        "demo_fallback", "sparse", "missing", "disabled", "explicit_empty", "scope_blocked",
    )]

    omi = next(s for s in sources if s["id"] == "omi_vault")
    if omi["status"] == "connected":
        primary_source = "omi_vault"
    elif omi["status"] == "demo":
        primary_source = "demo_fallback"
    elif omi["status"] == "explicit_empty":
        primary_source = "explicit_empty"
    elif omi["status"] == "scope_blocked":
        primary_source = "scope_blocked"
    else:
        primary_source = "omi_vault"

    return {
        "version": "1.1",
        "data_mode": data_mode,
        "vault_path": str(vault),
        "summary": {
            "connected_sources": connected,
            "needs_setup": missing,
            "primary_source": primary_source,
            "optional_enrichment": ["apple_health", "host_context", "condition_packs"],
        },
        "sources": sources,
        "catalog": SOURCE_CATALOG,
        "analysis_pipeline": ANALYSIS_PIPELINE,
        "tool_resource_map": TOOL_RESOURCE_MAP,
        "quick_setup": {
            "demo": [
                "cd code/health-mcp-starter && ./run-demo.sh",
                "Uses demo-data/vault — no real Omi needed",
            ],
            "real_omi": [
                "export OMI_VAULT_PATH=\"/path/to/Obsidian Vault\"",
                "./issue-sidecar.sh sleep-stress-sidecar",
                "python3 health-pattern-mcp.py",
            ],
            "real_apple": [
                "Health app → Export All Health Data → unzip to ~/Downloads/apple_health_export/",
                "Re-run analyze_lifestyle_patterns — overlap_days should increase",
            ],
        },
    }


def get_analysis_mechanics() -> Dict[str, Any]:
    """Pipeline-only view for docs / UI «как работает анализ»."""
    return {
        "pipeline": ANALYSIS_PIPELINE,
        "tool_resource_map": TOOL_RESOURCE_MAP,
        "principles": [
            "Local-first: raw transcripts never leave disk unless Azure opt-in with consent",
            "Scoped read: sidecar manifest ACL on every file",
            "Citations required: every insight links to date + excerpt or computed stat",
            "Personal baselines: compare to YOUR history, not population averages",
            "Audit trail: audit.log records tool + files on every access",
        ],
        "principles_ru": [
            "Local-first: сырые транскрипты не покидают диск без consent на Azure",
            "Scoped read: ACL манифеста на каждый файл",
            "Цитаты обязательны: каждый инсайт → дата + excerpt или stat",
            "Личные baseline: сравнение с ВАШЕЙ историей, не с нормами популяции",
            "Audit trail: audit.log фиксирует tool + files при каждом доступе",
        ],
    }
