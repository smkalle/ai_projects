from __future__ import annotations

import time

from fastapi.testclient import TestClient

from agent_eval.api import app


client = TestClient(app)


def _wait_for_run(run_id: str, timeout_s: float = 5.0) -> dict:
    deadline = time.time() + timeout_s
    detail = client.get(f"/api/runs/{run_id}").json()
    while detail["run"]["status"] == "running" and time.time() < deadline:
        time.sleep(0.05)
        detail = client.get(f"/api/runs/{run_id}").json()
    return detail


def test_health_meta_and_empty_safe_aggregates() -> None:
    assert client.get("/api/health").json() == {"status": "ok"}

    meta = client.get("/api/meta").json()
    assert "rule-based-v1" in meta["models"]
    assert "tutorial_basics_v1" in meta["scenarios"]
    assert "balanced" in meta["rubrics"]
    assert meta["default_profile"]["enabled_tools"]

    readout = client.post("/api/vc-readout", json=[]).json()
    assert readout["coverage"]["models"] == 0
    assert readout["coverage"]["total_cases"] == 0
    assert readout["readiness"] == "promising"


def test_single_run_detail_report_analytics_and_audit_workflow() -> None:
    response = client.post(
        "/api/runs",
        json={
            "profile": {"model": "rule-based-v1"},
            "config": {"dataset_id": "tutorial_basics_v1", "rubric_variant": "balanced", "retries": 0},
            "only_case_ids": ["calc_01"],
        },
    )
    run_id = response.json()["run_id"]
    detail = _wait_for_run(run_id)

    assert detail["run"]["status"] == "finished"
    assert detail["run"]["metrics_summary"]["total_cases"] == 1
    assert detail["cases"][0]["case_id"] == "calc_01"
    assert detail["cases"][0]["status"] == "passed"
    assert any(event["event_type"] == "run_finished" for event in detail["events"])

    report = client.get(f"/api/runs/{run_id}/report").json()
    assert run_id == report["run_id"]
    assert "Technical Evaluation Report" in report["report"]
    assert "calc_01" in report["report"]

    analytics = client.get("/api/analytics?limit=25").json()
    assert analytics["summary"]["total_runs"] >= 1
    assert analytics["summary"]["total_cases"] >= 1
    assert any(row["name"] == "rule-based-v1" for row in analytics["by_model"])

    audit = client.get("/api/audit?limit=25").json()
    assert any(event["run_id"] == run_id and event["event_type"] == "run_finished" for event in audit["events"])


def test_matrix_batch_vc_readout_and_support_workflow() -> None:
    response = client.post(
        "/api/matrix-runs",
        json={
            "profile": {"model": "rule-based-v1"},
            "config": {"rubric_variant": "balanced", "retries": 0},
            "models": ["rule-based-v1", "rule-based-v2"],
            "scenarios": ["tutorial_basics_v1", "tutorial_regression_v1"],
        },
    )
    run_ids = response.json()["run_ids"]
    assert len(run_ids) == 4
    details = [_wait_for_run(run_id) for run_id in run_ids]
    assert {detail["run"]["status"] for detail in details} == {"finished"}

    readout = client.post("/api/vc-readout", json=run_ids).json()
    assert readout["coverage"]["models"] == 2
    assert readout["coverage"]["scenarios"] == 2
    assert readout["coverage"]["total_cases"] == 16
    assert readout["coverage"]["weighted_pass_rate"] == 1.0
    assert readout["readiness"] == "demo_ready"
    assert len(readout["leaderboard"]) == 2
    assert len(readout["matrix"]) == 4

    support = client.post(
        "/api/support",
        json={
            "prompt": "From tutorial facts, what framework powers the console?",
            "profile": {"model": "rule-based-v1"},
        },
    ).json()
    assert support["answer"] == "streamlit"
    assert support["steps"][0]["tool_name"] == "lookup"


def test_unknown_run_returns_404() -> None:
    response = client.get("/api/runs/not_a_real_run")
    assert response.status_code == 404
