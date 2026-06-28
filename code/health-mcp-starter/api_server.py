#!/usr/bin/env python3
"""Local VitaSide dashboard API.

Thin FastAPI wrapper over the existing MCP module. It intentionally keeps all
health parsing and analytics inside health-pattern-mcp.py.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, Query, UploadFile, File, Form  # type: ignore[import-not-found]
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import-not-found]
from fastapi.responses import FileResponse, JSONResponse  # type: ignore[import-not-found]
from pydantic import BaseModel  # type: ignore[import-not-found]

from user_context import (
    add_manual_log,
    delete_manual_log,
    load_context,
    replace_list,
    save_context,
    summarize_context,
    update_profile,
    write_context_note,
)
from context_suggestions import apply_suggestions, diff_against_saved, extract_suggestions
from next_steps import build_next_steps


ROOT = Path(__file__).resolve().parent
os.environ.setdefault("OMI_VAULT_PATH", str(ROOT / "demo-data" / "vault"))
os.environ.setdefault("VITASIDE_MANIFEST", str(ROOT / "sidecars/sleep-stress-sidecar/manifest.yaml"))


def _load_vita():
    spec = importlib.util.spec_from_file_location("vita", ROOT / "health-pattern-mcp.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


vita = _load_vita()

app = FastAPI(
    title="VitaSide Local Dashboard API",
    version="1.0",
    description="Local-only JSON API for the VitaSide dashboard.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8787",
        "http://127.0.0.1:8787",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExportRequest(BaseModel):
    anonymize: bool = False


class AzureEnhanceRequest(BaseModel):
    user_consent: bool = True
    anonymize: bool = True
    prompt_hint: str = ""
    locale: str = "en"


class ProfileRequest(BaseModel):
    profile: Dict[str, Any]


class ContextListRequest(BaseModel):
    items: List[Dict[str, Any]]


class ManualLogRequest(BaseModel):
    date: str = ""
    type: str = "note"
    text: str
    severity: str = ""
    tags: List[str] = []



class SkinPhotoRequest(BaseModel):
    user_consent: bool = False
    use_external: bool = False

class ApplySuggestionsRequest(BaseModel):
    mode: str = "fill_empty"


class ApiError(BaseModel):
    error: str
    message: str = ""
    disclaimer: str = ""


_API_MODELS = (
    ExportRequest,
    AzureEnhanceRequest,
    ProfileRequest,
    ContextListRequest,
    ManualLogRequest,
    SkinPhotoRequest,
    ApplySuggestionsRequest,
    ApiError,
)


def _rebuild_pydantic_models() -> None:
    """Resolve forward refs when loaded via importlib under a non-canonical name."""
    _ns = globals()
    for _cls in _API_MODELS:
        _cls.model_rebuild(_types_namespace=_ns)


_rebuild_pydantic_models()

API_ERROR_404 = {404: {"model": ApiError, "description": "Resource not found"}}
API_ERROR_500 = {500: {"model": ApiError, "description": "Handler error"}}
API_ERROR_400 = {400: {"model": ApiError, "description": "Bad request"}}


def _with_error(fn):
    try:
        return fn()
    except Exception as exc:  # API boundary: return readable local errors to UI
        return JSONResponse(
            status_code=500,
            content={"error": type(exc).__name__, "message": str(exc)},
        )


def _latest_report(kind: str) -> str | None:
    pattern = f"vitaside-{kind}-*.html"
    files = sorted((ROOT / "out").glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0].name if files else None


@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {
        "ok": True,
        "version": "1.0",
        "root": str(ROOT),
        "demo_vault": str(ROOT / "demo-data" / "vault"),
    }


@app.get("/api/briefing", responses=API_ERROR_500)
def briefing() -> Dict[str, Any]:
    def build():
        result = vita.get_actionable_briefing()
        result["manual_context"] = summarize_context()
        return result

    return _with_error(build)


@app.get("/api/smart")
def smart() -> Dict[str, Any]:
    return _with_error(lambda: vita.smart_analysis())


@app.get("/api/data-sources")
def data_sources() -> Dict[str, Any]:
    return _with_error(lambda: vita.list_data_sources())


@app.get("/api/analysis-mechanics")
def analysis_mechanics() -> Dict[str, Any]:
    return _with_error(lambda: vita.get_analysis_mechanics())


@app.get("/api/narrative")
def narrative(locale: str = Query(default="en")) -> Dict[str, Any]:
    return _with_error(lambda: vita.get_local_narrative(locale))


@app.get("/api/timeline")
def timeline(limit: int = Query(default=90, ge=1, le=365)) -> Dict[str, Any]:
    def build():
        entries = vita._scan_omi(limit, tool="ui_timeline")
        rows = []
        for entry in sorted(entries, key=lambda e: e.get("date", "")):
            rows.append({
                "date": entry.get("date"),
                "signals": entry.get("signals", []),
                "sleep_quality": entry.get("sleep_quality", "unknown"),
                "snippet": entry.get("snippet", ""),
                "quality": entry.get("quality", 0),
                "parser_confidence": entry.get("parser_confidence"),
                "quality_warnings": entry.get("quality_warnings") or [],
                "low_quality_excerpt": entry.get("low_quality_excerpt", False),
                "time_of_day": entry.get("time_of_day"),
            })
        return {"count": len(rows), "entries": rows, "disclaimer": vita.DISCLAIMER}

    return _with_error(build)


@app.get("/api/condition-packs")
def condition_packs() -> Dict[str, Any]:
    return _with_error(lambda: vita.list_condition_packs())


@app.get("/api/condition/{condition_id}")
def condition(condition_id: str, days: int = Query(default=90, ge=7, le=365)) -> Dict[str, Any]:
    return _with_error(lambda: vita.track_condition(condition_id, days))


@app.get("/api/sidecar")
def sidecar() -> Dict[str, Any]:
    return _with_error(lambda: vita.get_sidecar_status())


@app.get("/api/user-context")
def user_context() -> Dict[str, Any]:
    return _with_error(lambda: {"context": load_context(), "summary": summarize_context()})


@app.put("/api/user-context")
def put_user_context(context: Dict[str, Any]) -> Dict[str, Any]:
    return _with_error(lambda: {"context": save_context(context), "summary": summarize_context()})


@app.put("/api/user-context/profile")
def put_profile(req: ProfileRequest) -> Dict[str, Any]:
    return _with_error(lambda: {"context": update_profile(req.profile), "summary": summarize_context()})


@app.put("/api/user-context/{kind}")
def put_context_list(kind: str, req: ContextListRequest) -> Dict[str, Any]:
    return _with_error(lambda: {"context": replace_list(kind, req.items), "summary": summarize_context()})


@app.post("/api/manual-logs")
def post_manual_log(req: ManualLogRequest) -> Dict[str, Any]:
    payload = req.model_dump()
    if not payload.get("date"):
        payload.pop("date", None)
    return _with_error(lambda: {"context": add_manual_log(payload), "summary": summarize_context()})


@app.delete("/api/manual-logs/{log_id}")
def delete_log(log_id: str) -> Dict[str, Any]:
    return _with_error(lambda: {"context": delete_manual_log(log_id), "summary": summarize_context()})


def _gather_suggestions() -> Dict[str, Any]:
    entries = vita._scan_omi(120, tool="context_suggestions")
    briefing = vita.get_actionable_briefing()
    raw = extract_suggestions(entries, briefing)
    pending = diff_against_saved(raw)
    return {"raw": raw, "pending": pending}


@app.get("/api/context-suggestions")
def context_suggestions() -> Dict[str, Any]:
    return _with_error(_gather_suggestions)


@app.post("/api/context-suggestions/apply")
def apply_context_suggestions(req: ApplySuggestionsRequest) -> Dict[str, Any]:
    def build():
        pending = _gather_suggestions()["pending"]
        result = apply_suggestions(pending, mode=req.mode)
        result["summary"] = summarize_context()
        return result

    return _with_error(build)


@app.get("/api/next-steps")
def next_steps(condition_id: str = Query(default="migraine")) -> Dict[str, Any]:
    def build():
        entries = vita._scan_omi(120, tool="next_steps")
        briefing = vita.get_actionable_briefing()
        pending = _gather_suggestions()["pending"]
        summary = summarize_context()
        try:
            condition = vita.track_condition(condition_id, 90)
        except Exception:
            condition = {}
        qs = vita.generate_visit_questions()
        steps = build_next_steps(
            briefing=briefing,
            context_summary=summary,
            suggestions_pending=pending,
            condition=condition,
            questions_count=qs.get("count", 0),
        )
        return {
            "steps": steps,
            "context_summary": summary,
            "pending_suggestions": sum(len(pending.get(k, [])) for k in ("conditions", "medications", "goals", "manual_logs")),
            "days_analyzed": briefing.get("days_analyzed", len({e.get("date") for e in entries if e.get("date")})),
        }

    return _with_error(build)


@app.get("/api/journals")
def journals_api() -> Dict[str, Any]:
    return _with_error(lambda: vita.list_journals())


@app.get("/api/headache-insights")
def headache_insights_api(max_lag: int = Query(default=2, ge=1, le=3)) -> Dict[str, Any]:
    return _with_error(lambda: vita.headache_insights(max_lag=max_lag))


@app.get("/api/journals/{journal_id}")
def journal_summary_api(journal_id: str) -> Dict[str, Any]:
    return _with_error(lambda: vita.journal_summary(journal_id))


@app.get("/api/questions")
def questions() -> Dict[str, Any]:
    def build():
        result = vita.generate_visit_questions()
        result["manual_context"] = summarize_context()
        return result

    return _with_error(build)


@app.get("/api/clinical-summary")
def clinical_summary_api() -> Dict[str, Any]:
    return _with_error(lambda: vita.get_clinical_summary())


@app.get("/api/n1-compare")
def n1_compare_api(
    exposure_signal: str = Query(default="stress"),
    outcome_signal: str = Query(default="mood_low"),
    window_days: int = Query(default=2, ge=0, le=7),
) -> Dict[str, Any]:
    return _with_error(
        lambda: vita.run_n1_compare(exposure_signal, outcome_signal, window_days)
    )


@app.get("/api/fhir-preview")
def fhir_preview_api(anonymize: bool = Query(default=False)) -> Dict[str, Any]:
    return _with_error(lambda: vita.export_fhir_bundle(anonymize=anonymize))


@app.post("/api/export-bundle")
def export_bundle(req: ExportRequest) -> Dict[str, Any]:
    def build():
        result = vita.export_visit_bundle(anonymize=req.anonymize)
        context_note = write_context_note()
        result["latest"] = {
            "patient_html": _latest_report("report"),
            "doctor_html": _latest_report("doctor"),
            "user_context": context_note.name,
        }
        result["manual_context"] = summarize_context()
        return result

    return _with_error(build)


@app.get("/api/reports/{filename}", responses=API_ERROR_404)
def report_file(filename: str):
    path = (ROOT / "out" / filename).resolve()
    if not str(path).startswith(str((ROOT / "out").resolve())) or not path.exists():
        return JSONResponse(status_code=404, content={"error": "not_found", "message": filename})
    return FileResponse(path)


@app.get("/api/azure-contract")
def azure_contract() -> Dict[str, Any]:
    return _with_error(lambda: vita.get_azure_contract())


@app.get("/api/preview-azure")
def preview_azure(
    operation: str = "enhance_insight",
    user_consent: bool = True,
    anonymize: bool = True,
) -> Dict[str, Any]:
    return _with_error(lambda: vita.preview_azure_payload(operation, user_consent, anonymize))


@app.post("/api/azure/enhance")
def azure_enhance(req: AzureEnhanceRequest) -> Dict[str, Any]:
    return _with_error(
        lambda: vita.azure_enhance_insight(
            user_consent=req.user_consent,
            anonymize=req.anonymize,
            prompt_hint=req.prompt_hint,
            locale=req.locale,
        )
    )



import tempfile

_SKIN_MAX_BYTES = 15 * 1024 * 1024  # 15 MB upload guard for skin photos


@app.post("/api/analyze-skin-photo", responses={**API_ERROR_400, **API_ERROR_500})
async def analyze_skin_photo_api(
    file: UploadFile = File(...),
    user_consent: bool = Form(False),
    use_external: bool = Form(False)
) -> Dict[str, Any]:
    """Upload skin photo for local ABCDE description (NOT a diagnosis or risk score)."""
    if not user_consent:
        return JSONResponse(
            status_code=400,
            content={
                "error": "user_consent is required",
                "disclaimer": "Consent required for analysis.",
            },
        )

    # Stream with a size guard so a huge upload cannot exhaust memory/disk.
    content = await file.read()
    if len(content) == 0:
        return JSONResponse(
            status_code=400,
            content={"error": "empty file", "disclaimer": "No image content received."},
        )
    if len(content) > _SKIN_MAX_BYTES:
        return JSONResponse(
            status_code=400,
            content={
                "error": f"file too large (max {_SKIN_MAX_BYTES // (1024*1024)} MB)",
                "disclaimer": "Use a smaller or compressed image.",
            },
        )

    suffix = Path(file.filename or "photo.jpg").suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = Path(tmp.name)
        tmp.write(content)

    try:
        result = vita.analyze_skin_photo(
            image_path=str(tmp_path),
            user_consent=True,
            use_external=use_external
        )
        result["original_filename"] = file.filename
        # Validation/processing errors from the analyzer come back as an "error"
        # field in the body — surface them as a 400 instead of a misleading 200.
        if result.get("error"):
            return JSONResponse(status_code=400, content=result)
        return result
    except Exception as exc:  # noqa: BLE001 — never leak a stack trace to the client
        return JSONResponse(
            status_code=500,
            content={"error": "analysis_failed", "disclaimer": "Skin analysis could not complete."},
        )
    finally:
        try:
            tmp_path.unlink()
        except Exception:  # noqa: BLE001
            pass

@app.get("/api/multi-source")
def multi_source() -> Dict[str, Any]:
    """Multi-source collector: notes + agent + wearables + omi + doctor_device.

    Unified, local-first collection. The doctor_device source is the innovation:
    a doctor-prescribed temporary sensor with a proactive agent collection window.
    """
    try:
        from multi_source_collector import MultiSourceCollector
        vault = os.environ.get("OMI_VAULT_PATH", str(ROOT / "demo-data" / "vault"))
        sources = ["notes", "agent", "wearables", "omi", "doctor_device", "frame_glasses"]
        col = MultiSourceCollector(vault, [s for s in sources if s != "frame_glasses"])
        events = col.collect_all()
        counts: Dict[str, int] = {}
        for e in events:
            counts[e.source] = counts.get(e.source, 0) + 1
        keymap = {"notes": "obsidian", "agent": "agent_hermes", "wearables": "apple_health", "omi": "omi", "doctor_device": "doctor_device", "frame_glasses": "frame_glasses"}
        labels = {
            "obsidian": "Obsidian notes",
            "agent_hermes": "Agent (Hermes)",
            "apple_health": "Wearables (Apple Health)",
            "omi": "Omi voice transcripts",
            "doctor_device": "Doctor-prescribed device",
            "frame_glasses": "Frame glasses (vision)",
        }
        # Real notes count from the actual vault scan (collector stub is a placeholder).
        try:
            notes_count = len(vita._scan_omi(120, tool="multi_source"))
        except Exception:
            notes_count = counts.get("obsidian", 0)
        # Frame glasses captures from the ~/vitaside integration (vision lifestyle capture).
        frame_captures = 0
        try:
            frame_jsonl = Path.home() / "vitaside" / "data" / "lifestyle_events.jsonl"
            if frame_jsonl.exists():
                with open(frame_jsonl) as fh:
                    frame_captures = sum(1 for _ in fh)
        except Exception:
            pass
        src_list = []
        for s in sources:
            key = keymap.get(s, s)
            if s == "frame_glasses":
                ev = frame_captures
            elif s == "notes":
                ev = notes_count
            else:
                ev = counts.get(key, 0)
            src_list.append({
                "id": s,
                "label": labels.get(key, s),
                "status": "connected" if (s != "frame_glasses" or frame_captures > 0) else "available",
                "events": ev,
                "proactive": s == "doctor_device",
            })
        return {
            "sources": src_list,
            "total_events": len(events),
            "doctor_device_active": counts.get("doctor_device", 0) > 0,
            "local": True,
            "disclaimer": "All sources processed locally. Doctor-device collection is temporary and manifest-gated.",
        }
    except Exception as exc:  # API boundary
        return {"error": "multi_source_failed", "message": str(exc), "sources": [], "total_events": 0}


@app.get("/api/frame-glasses")
def frame_glasses() -> Dict[str, Any]:
    """Frame glasses (Brilliant Labs) vision lifestyle capture integration.

    Reads the ~/vitaside integration data: capture events, lifestyle patterns,
    and the doctor summary. All local-first.
    """
    import json as _json
    try:
        data_dir = Path.home() / "vitaside" / "data"
        events_path = data_dir / "lifestyle_events.jsonl"
        patterns_path = data_dir / "patterns.json"
        summary_files = sorted(data_dir.glob("doctor_summary_*.json"))
        captures = 0
        recent: List[Dict[str, Any]] = []
        if events_path.exists():
            with open(events_path) as fh:
                lines = [ln for ln in fh.readlines() if ln.strip()]
            captures = len(lines)
            recent = [_json.loads(ln) for ln in lines[-3:]]
        patterns: Dict[str, Any] = {}
        if patterns_path.exists():
            patterns = _json.loads(patterns_path.read_text())
        summary: Dict[str, Any] = {}
        if summary_files:
            summary = _json.loads(summary_files[-1].read_text())
        return {
            "connected": captures > 0,
            "captures": captures,
            "top_tags": (patterns.get("top_tags") or [])[:6],
            "activity_distribution": patterns.get("activity_distribution", {}),
            "location_distribution": patterns.get("location_distribution", {}),
            "recommendation": patterns.get("recommendation_for_doctor", ""),
            "goals_alignment": patterns.get("goals_alignment", ""),
            "recent": [
                {"timestamp": e.get("timestamp"), "tags": e.get("lifestyle_tags", []), "activity": e.get("activity_level"), "location": e.get("location_type")}
                for e in recent
            ],
            "doctor_summary": summary,
            "local": True,
            "disclaimer": "Frame glasses vision capture. All processing local; export only on approval.",
        }
    except Exception as exc:  # API boundary
        return {"connected": False, "captures": 0, "error": "frame_unavailable", "message": str(exc)}


if __name__ == "__main__":
    import uvicorn  # type: ignore[import-not-found]

    uvicorn.run(app, host="127.0.0.1", port=8787)
