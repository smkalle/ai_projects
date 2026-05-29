from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def build_technical_report(run: dict[str, Any], cases: list[dict[str, Any]], events: list[dict[str, Any]]) -> str:
    metrics = run.get("metrics_summary") or {}
    profile = run.get("agent_profile") or {}
    config = run.get("eval_config") or {}
    passed = [case for case in cases if case.get("status") == "passed"]
    failed = [case for case in cases if case.get("status") != "passed"]
    tool_failures = [
        case
        for case in cases
        if not (case.get("assertions") or {}).get("tool_compliance", True)
    ]
    slowest = sorted(cases, key=lambda case: case.get("latency_ms", 0), reverse=True)[:5]

    lines = [
        f"# Technical Evaluation Report: {run.get('run_id', 'unknown')}",
        "",
        "## Result Summary",
        "",
        f"- Status: {run.get('status', 'unknown')}",
        f"- Created at: {run.get('created_at', 'unknown')}",
        f"- Dataset: {run.get('dataset_id', 'unknown')}",
        f"- Git SHA: {run.get('git_sha', 'unknown')}",
        f"- Model: {profile.get('model', 'unknown')}",
        f"- Rubric: {config.get('rubric_variant', metrics.get('rubric_variant', 'unknown'))}",
        f"- Total cases: {metrics.get('total_cases', len(cases))}",
        f"- Passed: {metrics.get('passed', len(passed))}",
        f"- Failed: {metrics.get('failed', len(failed))}",
        f"- Pass rate: {metrics.get('pass_rate', 0.0) * 100:.1f}%",
        f"- Average score: {metrics.get('avg_score', 0.0)}",
        f"- Average latency: {metrics.get('avg_latency_ms', 0)} ms",
        "",
        "## Technical Assessment",
        "",
    ]

    if failed:
        lines.append(f"{len(failed)} case(s) failed and should be inspected before promotion.")
    else:
        lines.append("All completed cases passed under the selected rubric.")
    if tool_failures:
        lines.append(f"{len(tool_failures)} case(s) did not use the expected tool set.")
    else:
        lines.append("Expected tool usage matched for all completed cases.")
    lines.extend(
        [
            "",
            "## Case Results",
            "",
            "| Case | Status | Score | Latency | Answer |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for case in cases:
        answer = str(case.get("answer", "")).replace("|", "\\|")
        lines.append(
            f"| {case.get('case_id', '')} | {case.get('status', '')} | "
            f"{case.get('score', 0.0)} | {case.get('latency_ms', 0)} ms | {answer} |"
        )

    if failed:
        lines.extend(["", "## Failed Case Details", ""])
        for case in failed:
            assertions = case.get("assertions") or {}
            lines.extend(
                [
                    f"### {case.get('case_id', 'unknown')}",
                    "",
                    f"- Expected answer: {assertions.get('expected_answer', '')}",
                    f"- Actual answer: {assertions.get('actual_answer', case.get('answer', ''))}",
                    f"- Expected tools: {', '.join(assertions.get('expected_tools', [])) or 'none'}",
                    f"- Used tools: {', '.join(assertions.get('used_tools', [])) or 'none'}",
                    f"- Exact match: {assertions.get('exact_match', False)}",
                    f"- Tool compliance: {assertions.get('tool_compliance', False)}",
                    "",
                ]
            )

    lines.extend(["", "## Latency Hotspots", ""])
    if slowest:
        for case in slowest:
            lines.append(f"- {case.get('case_id', 'unknown')}: {case.get('latency_ms', 0)} ms")
    else:
        lines.append("- No case latency data available.")

    event_counts: dict[str, int] = {}
    for event in events:
        event_type = event.get("event_type", "unknown")
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
    lines.extend(["", "## Event Coverage", ""])
    for event_type, count in sorted(event_counts.items()):
        lines.append(f"- {event_type}: {count}")

    return "\n".join(lines) + "\n"


def export_run_json(path: str | Path, run: dict[str, Any], cases: list[dict[str, Any]], events: list[dict[str, Any]]) -> str:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"run": run, "cases": cases, "events": events}, indent=2), encoding="utf-8")
    return str(out)


def export_cases_csv(path: str | Path, cases: list[dict[str, Any]]) -> str:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(cases).to_csv(out, index=False)
    return str(out)


def export_technical_report(path: str | Path, run: dict[str, Any], cases: list[dict[str, Any]], events: list[dict[str, Any]]) -> str:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_technical_report(run, cases, events), encoding="utf-8")
    return str(out)
