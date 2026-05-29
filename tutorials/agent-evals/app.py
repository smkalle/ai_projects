from __future__ import annotations

from pathlib import Path
import json
from dataclasses import asdict, replace
import time

import pandas as pd
import streamlit as st

from agent_eval.background import BackgroundRunManager
from agent_eval.config import AgentProfile, EvalConfig
from agent_eval.dataset import DATASET_OPTIONS
from agent_eval.reporting import build_technical_report, export_cases_csv, export_run_json, export_technical_report
from agent_eval.runner import EvalRunner
from agent_eval.scoring import RUBRIC_OPTIONS, apply_rubric_variant
from agent_eval.storage import EvalRepository


MODEL_OPTIONS = ["rule-based-v1", "rule-based-v2", "openai:gpt-5.4-mini"]


st.set_page_config(page_title="Agent Admin + Eval Console", layout="wide")

@st.cache_resource
def _services() -> tuple[EvalRepository, EvalRunner, BackgroundRunManager]:
    repository = EvalRepository("./eval_runs.db")
    eval_runner = EvalRunner(repository)
    return repository, eval_runner, BackgroundRunManager(eval_runner)


repo, runner, background_runs = _services()

st.title("Agent Admin and Evaluation Validation Console")
st.caption("Tutorial-focused agent controls, run orchestration, and step-level validation")


def _controls() -> tuple[AgentProfile, EvalConfig, list[str], list[str], list[str]]:
    st.sidebar.header("Agent Controls")
    profile_name = st.sidebar.text_input("Profile name", value="tutorial-agent")
    model = st.sidebar.selectbox(
        "Primary model",
        MODEL_OPTIONS,
        index=0,
    )
    matrix_models = st.sidebar.multiselect(
        "Models for comparison",
        MODEL_OPTIONS,
        default=[model],
    )
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.0, 0.1)
    max_steps = st.sidebar.slider("Max steps", 1, 8, 4)

    enabled_tools = st.sidebar.multiselect(
        "Enabled tools",
        ["calculator", "lookup", "format_json"],
        default=["calculator", "lookup", "format_json"],
    )

    st.sidebar.header("Eval Settings")
    dataset_ids = list(DATASET_OPTIONS)
    dataset_id = st.sidebar.selectbox(
        "Primary scenario",
        dataset_ids,
        index=0,
        format_func=lambda value: DATASET_OPTIONS[value],
    )
    matrix_scenarios = st.sidebar.multiselect(
        "Scenarios for comparison",
        dataset_ids,
        default=dataset_ids,
        format_func=lambda value: DATASET_OPTIONS[value],
    )
    rubric_ids = list(RUBRIC_OPTIONS)
    rubric_variant = st.sidebar.selectbox(
        "Rubric",
        rubric_ids,
        index=0,
        format_func=lambda value: RUBRIC_OPTIONS[value],
    )
    retries = st.sidebar.slider("Retries", 0, 3, 1)
    timeout_s = st.sidebar.slider("Timeout (seconds)", 5, 120, 30)
    fail_fast = st.sidebar.checkbox("Fail fast", value=False)
    semantic_grading = st.sidebar.checkbox("Semantic grading", value=True)

    case_filter = st.sidebar.text_input("Only case IDs (comma separated)", value="")
    only_case_ids = [s.strip() for s in case_filter.split(",") if s.strip()]

    profile = AgentProfile(
        name=profile_name,
        model=model,
        temperature=temperature,
        max_steps=max_steps,
        enabled_tools=enabled_tools,
    )
    config = EvalConfig(
        dataset_id=dataset_id,
        rubric_variant=rubric_variant,
        retries=retries,
        timeout_s=timeout_s,
        fail_fast=fail_fast,
        semantic_grading=semantic_grading,
    )
    apply_rubric_variant(config)
    return profile, config, only_case_ids, matrix_models or [model], matrix_scenarios or [dataset_id]


profile, config, only_case_ids, matrix_models, matrix_scenarios = _controls()


def _start_all_dataset_runs(profile: AgentProfile, config: EvalConfig) -> list[str]:
    run_ids = []
    for dataset_id in DATASET_OPTIONS:
        dataset_config = replace(config, dataset_id=dataset_id, fail_fast=False)
        run_ids.append(background_runs.start(profile, dataset_config))
    return run_ids


def _start_eval_matrix(
    profile: AgentProfile,
    config: EvalConfig,
    models: list[str],
    scenario_ids: list[str],
) -> list[str]:
    run_ids = []
    for model in models:
        model_profile = replace(profile, model=model)
        for scenario_id in scenario_ids:
            scenario_config = replace(config, dataset_id=scenario_id, fail_fast=False)
            run_ids.append(background_runs.start(model_profile, scenario_config))
    return run_ids


left, right = st.columns([2, 3])
with left:
    st.subheader("Run Actions")
    if st.button("Start Background Eval Run", type="primary", use_container_width=True):
        run_id = background_runs.start(profile, config, only_case_ids=only_case_ids or None)
        st.session_state["selected_run_id"] = run_id
        st.success(f"Run started: {run_id}")

    if st.button("Run All and Compare", use_container_width=True):
        run_ids = _start_all_dataset_runs(profile, config)
        st.session_state["selected_run_id"] = run_ids[0]
        st.session_state["compare_run_ids"] = run_ids
        st.success(f"Started {len(run_ids)} eval runs.")

    if st.button("Run Model x Scenario Matrix", use_container_width=True):
        run_ids = _start_eval_matrix(profile, config, matrix_models, matrix_scenarios)
        st.session_state["selected_run_id"] = run_ids[0]
        st.session_state["compare_run_ids"] = run_ids
        st.success(f"Started {len(run_ids)} matrix runs.")

    runs = repo.list_runs(limit=100)
    run_ids = [r["run_id"] for r in runs]
    default_run = st.session_state.get("selected_run_id")
    index = run_ids.index(default_run) if default_run in run_ids else 0
    selected_run_id = st.selectbox("Run history", run_ids, index=index if run_ids else None)
    if selected_run_id:
        st.session_state["selected_run_id"] = selected_run_id

with right:
    st.subheader("Current Config")
    st.code(
        json.dumps(
            {
                "agent": asdict(profile),
                "eval": config.to_dict(),
                "matrix": {"models": matrix_models, "scenarios": matrix_scenarios},
            },
            indent=2,
        ),
        language="json",
    )


def _render_summary(run_id: str) -> None:
    run = repo.get_run(run_id)
    if not run:
        st.info("No run selected")
        return

    metrics = run["metrics_summary"] or {}
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", metrics.get("total_cases", 0))
    c2.metric("Pass Rate", f"{metrics.get('pass_rate', 0.0) * 100:.1f}%")
    c3.metric("Avg Score", metrics.get("avg_score", 0.0))
    c4.metric("Avg Latency", f"{metrics.get('avg_latency_ms', 0)} ms")

    planned = metrics.get("planned_cases")
    if planned:
        st.progress(min(1.0, metrics.get("total_cases", 0) / planned))
    st.caption(
        f"Status: {run['status']} | Dataset: {run['dataset_id']} | "
        f"Rubric: {run['eval_config'].get('rubric_variant', 'balanced')} | Git SHA: {run['git_sha']}"
    )


def _render_console(run_id: str) -> None:
    events = repo.get_events(run_id)
    if not events:
        st.info("No events for this run")
        return

    for event in events:
        with st.expander(
            f"{event['event_type']} | case={event['case_id']} | step={event['step_idx']} | {event['status']}",
            expanded=event["event_type"] in {"case_finished", "run_finished"},
        ):
            st.write(f"timestamp: {event['timestamp']}")
            if event["duration_ms"]:
                st.write(f"duration: {event['duration_ms']} ms")
            st.json(event["payload"])


def _render_cases(run_id: str) -> None:
    cases = repo.get_case_results(run_id)
    if not cases:
        st.info("No case results")
        return
    df = pd.DataFrame(cases)
    st.dataframe(df[["case_id", "status", "score", "latency_ms", "answer"]], use_container_width=True)

    case_id = st.selectbox("Inspect case", [c["case_id"] for c in cases], index=0)
    selected = next(c for c in cases if c["case_id"] == case_id)
    st.json(selected["assertions"])


def _render_exports(run_id: str) -> None:
    run = repo.get_run(run_id)
    cases = repo.get_case_results(run_id)
    events = repo.get_events(run_id)
    out_dir = Path("./artifacts")

    report = build_technical_report(run, cases, events)
    st.subheader("Technical Report Preview")
    st.markdown(report)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Export JSON", use_container_width=True):
            path = export_run_json(out_dir / f"{run_id}.json", run, cases, events)
            st.success(f"Exported: {path}")
    with col2:
        if st.button("Export CSV", use_container_width=True):
            path = export_cases_csv(out_dir / f"{run_id}_cases.csv", cases)
            st.success(f"Exported: {path}")
    with col3:
        if st.button("Export Report", use_container_width=True):
            path = export_technical_report(out_dir / f"{run_id}_technical_report.md", run, cases, events)
            st.success(f"Exported: {path}")


def _run_label(run: dict) -> str:
    model = run.get("agent_profile", {}).get("model", "unknown")
    return f"{run.get('dataset_id', 'unknown')} | {model} | {run.get('run_id', '')}"


def _run_key(run: dict) -> str:
    model = run.get("agent_profile", {}).get("model", "unknown").replace(":", "_")
    scenario = run.get("dataset_id", "unknown")
    return f"{model}__{scenario}"


def _render_side_by_side_compare(run_ids: list[str]) -> None:
    selected_runs = [run for run in (repo.get_run(run_id) for run_id in run_ids) if run]
    if len(selected_runs) < 2:
        return

    st.subheader("Side-by-Side Summary")
    metric_cols = st.columns(len(selected_runs))
    for col, run in zip(metric_cols, selected_runs):
        metrics = run.get("metrics_summary") or {}
        with col:
            st.caption(_run_label(run))
            st.metric("Pass Rate", f"{metrics.get('pass_rate', 0.0) * 100:.1f}%")
            st.metric("Avg Score", metrics.get("avg_score", 0.0))
            st.metric("Avg Latency", f"{metrics.get('avg_latency_ms', 0)} ms")
            st.write(f"Status: {run.get('status', 'unknown')}")

    case_maps = {
        run["run_id"]: {case["case_id"]: case for case in repo.get_case_results(run["run_id"])}
        for run in selected_runs
    }
    case_ids = sorted({case_id for cases in case_maps.values() for case_id in cases})
    rows = []
    for case_id in case_ids:
        row = {"case_id": case_id}
        for run in selected_runs:
            label = _run_key(run)
            case = case_maps[run["run_id"]].get(case_id, {})
            row[f"{label}_status"] = case.get("status", "missing")
            row[f"{label}_score"] = case.get("score")
            row[f"{label}_latency_ms"] = case.get("latency_ms")
            row[f"{label}_answer"] = case.get("answer")
        rows.append(row)

    st.subheader("Side-by-Side Cases")
    st.dataframe(pd.DataFrame(rows), use_container_width=True)


def _matrix_dataframe(run_ids: list[str]) -> pd.DataFrame:
    rows = []
    for run_id in run_ids:
        run = repo.get_run(run_id)
        if not run:
            continue
        metrics = run.get("metrics_summary") or {}
        profile_data = run.get("agent_profile") or {}
        rows.append(
            {
                "run_id": run_id,
                "model": profile_data.get("model", "unknown"),
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
    return pd.DataFrame(rows)


def _render_vc_readout(run_ids: list[str]) -> None:
    selected_ids = [run_id for run_id in run_ids if repo.get_run(run_id)]
    if not selected_ids:
        st.info("Run a model x scenario matrix to generate the VC readout.")
        return

    df = _matrix_dataframe(selected_ids)
    if df.empty:
        st.info("No completed run data is available yet.")
        return

    completed = df[df["status"].isin(["finished", "finished_with_failures"])]
    source = completed if not completed.empty else df
    model_count = source["model"].nunique()
    scenario_count = source["scenario"].nunique()
    total_cases = int(source["total_cases"].sum())
    weighted_pass = (
        (source["pass_rate"] * source["total_cases"]).sum() / max(1, source["total_cases"].sum())
    )
    avg_latency = int(source["avg_latency_ms"].mean()) if not source.empty else 0

    st.subheader("VC Readout")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Models Covered", model_count)
    k2.metric("Scenarios Covered", scenario_count)
    k3.metric("Weighted Pass Rate", f"{weighted_pass * 100:.1f}%")
    k4.metric("Avg Latency", f"{avg_latency} ms")

    st.subheader("Investment-Style Signal")
    if weighted_pass >= 0.95 and source["failed"].sum() == 0:
        st.success("Ready for demo: all measured scenarios are passing with strong consistency.")
    elif weighted_pass >= 0.8:
        st.warning("Promising but not yet clean: investigate failing cases before using this as a reliability claim.")
    else:
        st.error("Not ready for external claims: current scenario coverage shows material quality risk.")

    st.subheader("Model Leaderboard")
    model_rows = (
        source.groupby("model", as_index=False)
        .agg(
            scenarios=("scenario", "nunique"),
            pass_rate=("pass_rate", "mean"),
            avg_score=("avg_score", "mean"),
            avg_latency_ms=("avg_latency_ms", "mean"),
            failed=("failed", "sum"),
        )
        .sort_values(["pass_rate", "avg_score", "avg_latency_ms"], ascending=[False, False, True])
    )
    st.dataframe(model_rows, use_container_width=True)

    st.subheader("Scenario Matrix")
    st.dataframe(source.sort_values(["scenario", "model"]), use_container_width=True)


def _render_comparison() -> None:
    runs = repo.list_runs(limit=100)
    run_ids = [r["run_id"] for r in runs]
    if len(run_ids) < 2:
        st.info("Run at least two evaluations to compare results.")
        return

    if st.button("Run All Datasets Now", use_container_width=True):
        new_run_ids = _start_all_dataset_runs(profile, config)
        st.session_state["selected_run_id"] = new_run_ids[0]
        st.session_state["compare_run_ids"] = new_run_ids
        st.success(f"Started {len(new_run_ids)} eval runs.")
        st.rerun()

    if st.button("Run Full Model x Scenario Matrix", use_container_width=True):
        new_run_ids = _start_eval_matrix(profile, config, matrix_models, matrix_scenarios)
        st.session_state["selected_run_id"] = new_run_ids[0]
        st.session_state["compare_run_ids"] = new_run_ids
        st.success(f"Started {len(new_run_ids)} matrix runs.")
        st.rerun()

    default_compare = [run_id for run_id in st.session_state.get("compare_run_ids", []) if run_id in run_ids]
    selected_compare = st.multiselect(
        "Side-by-side runs",
        run_ids,
        default=default_compare[:4] if default_compare else run_ids[:2],
        help="Use Run All and Compare to populate this with one run per dataset.",
    )
    if selected_compare:
        st.session_state["compare_run_ids"] = selected_compare
    if len(selected_compare) > 4:
        st.warning("Showing the first four selected runs to keep the side-by-side view readable.")
        selected_compare = selected_compare[:4]
    if len(selected_compare) >= 2:
        _render_side_by_side_compare(selected_compare)

    col1, col2 = st.columns(2)
    with col1:
        baseline_id = st.selectbox("Baseline run", run_ids, index=1, key="baseline_run")
    with col2:
        candidate_id = st.selectbox("Candidate run", run_ids, index=0, key="candidate_run")

    baseline = repo.get_run(baseline_id)
    candidate = repo.get_run(candidate_id)
    if not baseline or not candidate:
        st.info("Select two completed runs.")
        return

    base_metrics = baseline["metrics_summary"]
    cand_metrics = candidate["metrics_summary"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Pass Rate Delta", f"{(cand_metrics.get('pass_rate', 0) - base_metrics.get('pass_rate', 0)) * 100:.1f}%")
    c2.metric("Avg Score Delta", round(cand_metrics.get("avg_score", 0) - base_metrics.get("avg_score", 0), 4))
    c3.metric("Avg Latency Delta", f"{cand_metrics.get('avg_latency_ms', 0) - base_metrics.get('avg_latency_ms', 0)} ms")

    baseline_cases = {case["case_id"]: case for case in repo.get_case_results(baseline_id)}
    candidate_cases = {case["case_id"]: case for case in repo.get_case_results(candidate_id)}
    rows = []
    for case_id in sorted(set(baseline_cases) | set(candidate_cases)):
        base_case = baseline_cases.get(case_id, {})
        cand_case = candidate_cases.get(case_id, {})
        rows.append(
            {
                "case_id": case_id,
                "baseline_status": base_case.get("status", "missing"),
                "candidate_status": cand_case.get("status", "missing"),
                "baseline_score": base_case.get("score"),
                "candidate_score": cand_case.get("score"),
                "score_delta": round((cand_case.get("score") or 0) - (base_case.get("score") or 0), 4),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True)


current_run_id = st.session_state.get("selected_run_id")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Live Console", "Run Summary", "Case Explorer", "Exports", "Compare Runs", "VC Readout"]
)

with tab1:
    if current_run_id:
        _render_console(current_run_id)
    else:
        st.info("Start a run to see events.")

with tab2:
    if current_run_id:
        _render_summary(current_run_id)
    else:
        st.info("Select a run.")

with tab3:
    if current_run_id:
        _render_cases(current_run_id)
    else:
        st.info("Select a run.")

with tab4:
    if current_run_id:
        _render_exports(current_run_id)
    else:
        st.info("Select a run.")

with tab5:
    _render_comparison()

with tab6:
    _render_vc_readout(st.session_state.get("compare_run_ids", []))

active_run_ids = {current_run_id} if current_run_id else set()
active_run_ids.update(st.session_state.get("compare_run_ids", []))
if any((repo.get_run(run_id) or {}).get("status") == "running" for run_id in active_run_ids):
    st.toast("Eval run is still running; refreshing console.")
    time.sleep(1)
    st.rerun()
