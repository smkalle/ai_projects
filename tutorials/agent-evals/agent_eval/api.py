from __future__ import annotations

from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .agent import TutorialAgent
from .background import BackgroundRunManager
from .config import AgentProfile, EvalConfig
from .dataset import DATASET_OPTIONS
from .reporting import build_technical_report
from .runner import EvalRunner
from .scoring import RUBRIC_OPTIONS, apply_rubric_variant
from .storage import EvalRepository


MODEL_OPTIONS = ["rule-based-v1", "rule-based-v2", "openai:gpt-5.4-mini"]

repository = EvalRepository("./eval_runs.db")
runner = EvalRunner(repository)
background_runs = BackgroundRunManager(runner)

app = FastAPI(
    title="Agent Evals V2 API",
    version="2.0.0",
    description="Multi-model, multi-scenario evaluation API for the V2 dashboard.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    profile: dict[str, Any] = Field(default_factory=dict)
    config: dict[str, Any] = Field(default_factory=dict)
    only_case_ids: list[str] | None = None


class MatrixRunRequest(BaseModel):
    profile: dict[str, Any] = Field(default_factory=dict)
    config: dict[str, Any] = Field(default_factory=dict)
    models: list[str] = Field(default_factory=lambda: ["rule-based-v1", "rule-based-v2"])
    scenarios: list[str] = Field(default_factory=lambda: list(DATASET_OPTIONS))


class SupportRequest(BaseModel):
    prompt: str
    profile: dict[str, Any] = Field(default_factory=dict)


def _profile_from_payload(payload: dict[str, Any]) -> AgentProfile:
    fields = {key: payload[key] for key in AgentProfile.__dataclass_fields__ if key in payload}
    return AgentProfile(**fields)


def _config_from_payload(payload: dict[str, Any]) -> EvalConfig:
    fields = {key: payload[key] for key in EvalConfig.__dataclass_fields__ if key in payload}
    return apply_rubric_variant(EvalConfig(**fields))


def _run_detail(run_id: str) -> dict[str, Any]:
    run = repository.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Unknown run: {run_id}")
    return {
        "run": run,
        "cases": repository.get_case_results(run_id),
        "events": repository.get_events(run_id),
        "active": background_runs.is_active(run_id),
    }


def _matrix_rows(run_ids: list[str]) -> list[dict[str, Any]]:
    rows = []
    for run_id in run_ids:
        run = repository.get_run(run_id)
        if not run:
            continue
        metrics = run.get("metrics_summary") or {}
        profile = run.get("agent_profile") or {}
        rows.append(
            {
                "run_id": run_id,
                "model": profile.get("model", "unknown"),
                "scenario": run.get("dataset_id", "unknown"),
                "status": run.get("status", "unknown"),
                "pass_rate": metrics.get("pass_rate", 0.0),
                "avg_score": metrics.get("avg_score", 0.0),
                "avg_latency_ms": metrics.get("avg_latency_ms", 0),
                "passed": metrics.get("passed", 0),
                "failed": metrics.get("failed", 0),
                "total_cases": metrics.get("total_cases", 0),
            }
        )
    return rows


def _analytics(limit: int = 100) -> dict[str, Any]:
    runs = repository.list_runs(limit=limit)
    run_details = [repository.get_run(run["run_id"]) for run in runs]
    run_details = [run for run in run_details if run]
    total_runs = len(run_details)
    finished = [run for run in run_details if run["status"] in {"finished", "finished_with_failures"}]
    running = [run for run in run_details if run["status"] == "running"]
    failed_runs = [run for run in run_details if run["status"] == "failed"]
    total_cases = sum((run.get("metrics_summary") or {}).get("total_cases", 0) for run in finished)
    failures = sum((run.get("metrics_summary") or {}).get("failed", 0) for run in finished)
    weighted_pass_rate = (
        sum(
            (run.get("metrics_summary") or {}).get("pass_rate", 0.0)
            * (run.get("metrics_summary") or {}).get("total_cases", 0)
            for run in finished
        )
        / max(1, total_cases)
    )
    latencies = [(run.get("metrics_summary") or {}).get("avg_latency_ms", 0) for run in finished]

    by_model: dict[str, dict[str, Any]] = {}
    by_scenario: dict[str, dict[str, Any]] = {}
    for run in finished:
        metrics = run.get("metrics_summary") or {}
        model = (run.get("agent_profile") or {}).get("model", "unknown")
        scenario = run.get("dataset_id", "unknown")
        for key, bucket in ((model, by_model), (scenario, by_scenario)):
            bucket.setdefault(key, {"name": key, "runs": 0, "cases": 0, "failures": 0, "pass_rate_total": 0.0})
            bucket[key]["runs"] += 1
            bucket[key]["cases"] += metrics.get("total_cases", 0)
            bucket[key]["failures"] += metrics.get("failed", 0)
            bucket[key]["pass_rate_total"] += metrics.get("pass_rate", 0.0)

    def finalize(rows: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        values = []
        for row in rows.values():
            values.append(
                {
                    "name": row["name"],
                    "runs": row["runs"],
                    "cases": row["cases"],
                    "failures": row["failures"],
                    "avg_pass_rate": round(row["pass_rate_total"] / max(1, row["runs"]), 4),
                }
            )
        return sorted(values, key=lambda row: (-row["avg_pass_rate"], row["failures"], row["name"]))

    return {
        "summary": {
            "total_runs": total_runs,
            "finished_runs": len(finished),
            "running_runs": len(running),
            "failed_runs": len(failed_runs),
            "total_cases": total_cases,
            "case_failures": failures,
            "weighted_pass_rate": round(weighted_pass_rate, 4),
            "avg_latency_ms": int(sum(latencies) / max(1, len(latencies))),
        },
        "by_model": finalize(by_model),
        "by_scenario": finalize(by_scenario),
        "recent_runs": runs[:12],
    }


def _vc_readout(run_ids: list[str]) -> dict[str, Any]:
    rows = _matrix_rows(run_ids)
    completed = [row for row in rows if row["status"] in {"finished", "finished_with_failures"}]
    source = completed or rows
    total_cases = sum(row["total_cases"] for row in source)
    weighted_pass_rate = (
        sum(row["pass_rate"] * row["total_cases"] for row in source) / max(1, total_cases)
    )
    avg_latency_ms = int(sum(row["avg_latency_ms"] for row in source) / max(1, len(source)))
    total_failures = sum(row["failed"] for row in source)

    model_rollup: dict[str, dict[str, Any]] = {}
    for row in source:
        model = row["model"]
        model_rollup.setdefault(
            model,
            {"model": model, "scenarios": set(), "pass_rates": [], "scores": [], "latencies": [], "failed": 0},
        )
        model_rollup[model]["scenarios"].add(row["scenario"])
        model_rollup[model]["pass_rates"].append(row["pass_rate"])
        model_rollup[model]["scores"].append(row["avg_score"])
        model_rollup[model]["latencies"].append(row["avg_latency_ms"])
        model_rollup[model]["failed"] += row["failed"]

    leaderboard = []
    for value in model_rollup.values():
        leaderboard.append(
            {
                "model": value["model"],
                "scenarios": len(value["scenarios"]),
                "pass_rate": round(sum(value["pass_rates"]) / max(1, len(value["pass_rates"])), 4),
                "avg_score": round(sum(value["scores"]) / max(1, len(value["scores"])), 4),
                "avg_latency_ms": int(sum(value["latencies"]) / max(1, len(value["latencies"]))),
                "failed": value["failed"],
            }
        )
    leaderboard.sort(key=lambda row: (-row["pass_rate"], -row["avg_score"], row["avg_latency_ms"]))

    if not source:
        readiness = "promising"
        narrative = "No completed scenario coverage is available yet."
    elif weighted_pass_rate >= 0.95 and total_failures == 0:
        readiness = "demo_ready"
        narrative = "All measured scenarios are passing with strong consistency."
    elif weighted_pass_rate >= 0.8:
        readiness = "promising"
        narrative = "Promising coverage with remaining failures to investigate before external claims."
    else:
        readiness = "not_ready"
        narrative = "Current scenario coverage shows material quality risk."

    return {
        "coverage": {
            "models": len({row["model"] for row in source}),
            "scenarios": len({row["scenario"] for row in source}),
            "total_cases": total_cases,
            "weighted_pass_rate": round(weighted_pass_rate, 4),
            "avg_latency_ms": avg_latency_ms,
            "failures": total_failures,
        },
        "readiness": readiness,
        "narrative": narrative,
        "leaderboard": leaderboard,
        "matrix": rows,
    }


def _audit_events(limit: int = 80) -> list[dict[str, Any]]:
    runs = repository.list_runs(limit=40)
    events: list[dict[str, Any]] = []
    for run in runs:
        detail = repository.get_run(run["run_id"])
        if not detail:
            continue
        for event in repository.get_events(run["run_id"]):
            events.append(
                {
                    "run_id": run["run_id"],
                    "created_at": detail.get("created_at"),
                    "model": (detail.get("agent_profile") or {}).get("model", "unknown"),
                    "scenario": detail.get("dataset_id", "unknown"),
                    "event_type": event.get("event_type"),
                    "case_id": event.get("case_id"),
                    "status": event.get("status"),
                    "timestamp": event.get("timestamp"),
                    "payload": event.get("payload"),
                }
            )
    return sorted(events, key=lambda event: event.get("timestamp", ""), reverse=True)[:limit]


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/meta")
def meta() -> dict[str, Any]:
    return {
        "models": MODEL_OPTIONS,
        "scenarios": DATASET_OPTIONS,
        "rubrics": RUBRIC_OPTIONS,
        "default_profile": asdict(AgentProfile()),
        "default_config": EvalConfig().to_dict(),
    }


@app.get("/api/runs")
def list_runs(limit: int = 100) -> dict[str, Any]:
    runs = repository.list_runs(limit=limit)
    return {"runs": runs}


@app.get("/api/analytics")
def analytics(limit: int = 100) -> dict[str, Any]:
    return _analytics(limit=limit)


@app.get("/api/audit")
def audit(limit: int = 80) -> dict[str, Any]:
    return {"events": _audit_events(limit=limit)}


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    return _run_detail(run_id)


@app.post("/api/runs")
def start_run(request: RunRequest) -> dict[str, Any]:
    profile = _profile_from_payload(request.profile)
    config = _config_from_payload(request.config)
    run_id = background_runs.start(profile, config, only_case_ids=request.only_case_ids)
    return {"run_id": run_id}


@app.post("/api/matrix-runs")
def start_matrix_run(request: MatrixRunRequest) -> dict[str, Any]:
    profile = _profile_from_payload(request.profile)
    config = _config_from_payload(request.config)
    run_ids = []
    for model in request.models:
        model_profile = replace(profile, model=model)
        for scenario in request.scenarios:
            scenario_config = replace(config, dataset_id=scenario, fail_fast=False)
            run_ids.append(background_runs.start(model_profile, scenario_config))
    return {"run_ids": run_ids}


@app.post("/api/support")
def support(request: SupportRequest) -> dict[str, Any]:
    profile = _profile_from_payload(request.profile)
    result = TutorialAgent(profile).solve(request.prompt)
    return {
        "answer": result.answer,
        "steps": [asdict(step) for step in result.steps],
        "model": profile.model,
    }


@app.post("/api/vc-readout")
def vc_readout(run_ids: list[str]) -> dict[str, Any]:
    return _vc_readout(run_ids)


@app.get("/api/runs/{run_id}/report")
def run_report(run_id: str) -> dict[str, str]:
    detail = _run_detail(run_id)
    return {
        "run_id": run_id,
        "report": build_technical_report(detail["run"], detail["cases"], detail["events"]),
    }


frontend_dist = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")


@app.get("/", response_model=None)
def serve_frontend() -> Any:
    index = frontend_dist / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"service": "Agent Evals V2 API", "docs": "/docs", "frontend": "Run npm install && npm run dev in frontend/"}
