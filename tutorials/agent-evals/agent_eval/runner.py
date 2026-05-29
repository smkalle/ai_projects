from __future__ import annotations

from dataclasses import asdict
from time import perf_counter
import subprocess

from .agent import TutorialAgent
from .config import AgentProfile, EvalConfig
from .dataset import load_dataset
from .models import CaseResult, EvalRun, StepEvent
from .scoring import apply_rubric_variant, score_case
from .storage import EvalRepository


def _git_sha() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
    except Exception:
        return "unknown"


class EvalRunner:
    def __init__(self, repo: EvalRepository):
        self.repo = repo

    def create_run(self, profile: AgentProfile, config: EvalConfig) -> str:
        config = apply_rubric_variant(config)
        run = EvalRun(
            run_id=EvalRun.new_id(),
            status="running",
            dataset_id=config.dataset_id,
            agent_profile=asdict(profile),
            eval_config=config.to_dict(),
            git_sha=_git_sha(),
        )
        self.repo.create_run(run)
        return run.run_id

    def run(self, profile: AgentProfile, config: EvalConfig, only_case_ids: list[str] | None = None) -> str:
        run_id = self.create_run(profile, config)
        self.execute_run(run_id, profile, config, only_case_ids=only_case_ids)
        return run_id

    def execute_run(
        self,
        run_id: str,
        profile: AgentProfile,
        config: EvalConfig,
        only_case_ids: list[str] | None = None,
    ) -> None:
        config = apply_rubric_variant(config)
        self.repo.add_event(
            StepEvent(
                run_id=run_id,
                case_id="_run",
                step_idx=0,
                event_type="run_started",
                status="ok",
                payload={"dataset": config.dataset_id, "rubric": config.rubric_variant},
            )
        )

        cases = load_dataset(config.dataset_id)
        if only_case_ids:
            include = set(only_case_ids)
            cases = [c for c in cases if c.case_id in include]

        passed = 0
        failed = 0
        total_score = 0.0
        total_latency = 0
        agent = TutorialAgent(profile)

        for case_idx, case in enumerate(cases, start=1):
            self.repo.add_event(
                StepEvent(
                    run_id=run_id,
                    case_id=case.case_id,
                    step_idx=0,
                    event_type="case_started",
                    status="ok",
                    payload={"prompt": case.prompt, "attempt": 1, "case_index": case_idx, "total_cases": len(cases)},
                )
            )

            start = perf_counter()
            status = "passed"
            answer = ""
            used_tools: list[str] = []
            assertions = {}
            score = 0.0

            for attempt in range(config.retries + 1):
                start = perf_counter()
                used_tools = []
                answer = ""
                try:
                    if attempt > 0:
                        self.repo.add_event(
                            StepEvent(
                                run_id=run_id,
                                case_id=case.case_id,
                                step_idx=attempt,
                                event_type="case_retry",
                                status="ok",
                                payload={"attempt": attempt + 1},
                            )
                        )

                    result = agent.solve(case.prompt)
                    answer = result.answer

                    for step in result.steps:
                        if step.tool_name:
                            used_tools.append(step.tool_name)
                        self.repo.add_event(
                            StepEvent(
                                run_id=run_id,
                                case_id=case.case_id,
                                step_idx=step.step_idx,
                                event_type="step_finished",
                                status="ok",
                                payload={
                                    "summary": step.summary,
                                    "tool_name": step.tool_name,
                                    "tool_args": step.tool_args,
                                    "tool_output": step.tool_output,
                                    "attempt": attempt + 1,
                                },
                                duration_ms=step.duration_ms,
                            )
                        )

                    latency_ms = int((perf_counter() - start) * 1000)
                    scored = score_case(case, answer, used_tools, latency_ms, config)
                    assertions = scored.assertions | {"attempt": attempt + 1}
                    score = scored.score
                    status = "passed" if scored.passed else "failed"
                except Exception as exc:
                    latency_ms = int((perf_counter() - start) * 1000)
                    status = "failed"
                    assertions = {"error": str(exc), "attempt": attempt + 1}
                    score = 0.0

                if status == "passed" or attempt >= config.retries:
                    break

                self.repo.add_event(
                    StepEvent(
                        run_id=run_id,
                        case_id=case.case_id,
                        step_idx=998,
                        event_type="case_attempt_failed",
                        status="failed",
                        payload={"score": score, "answer": answer, "assertions": assertions},
                        duration_ms=latency_ms,
                    )
                )

            self.repo.add_case_result(
                CaseResult(
                    run_id=run_id,
                    case_id=case.case_id,
                    status=status,
                    score=score,
                    latency_ms=latency_ms,
                    answer=answer,
                    assertions=assertions,
                )
            )

            self.repo.add_event(
                StepEvent(
                    run_id=run_id,
                    case_id=case.case_id,
                    step_idx=999,
                    event_type="case_finished",
                    status=status,
                    payload={"score": score, "answer": answer, "assertions": assertions},
                    duration_ms=latency_ms,
                )
            )

            total_latency += latency_ms
            total_score += score
            if status == "passed":
                passed += 1
            else:
                failed += 1
                if config.fail_fast:
                    break

            current_total = passed + failed
            self.repo.update_run(
                run_id,
                "running",
                {
                    "total_cases": current_total,
                    "planned_cases": len(cases),
                    "passed": passed,
                    "failed": failed,
                    "pass_rate": round(passed / max(1, current_total), 4),
                    "avg_score": round(total_score / max(1, current_total), 4),
                    "avg_latency_ms": int(total_latency / max(1, current_total)),
                },
            )

        total = max(1, passed + failed)
        metrics = {
            "total_cases": passed + failed,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / total, 4),
            "avg_score": round(total_score / total, 4),
            "avg_latency_ms": int(total_latency / total),
            "rubric_variant": config.rubric_variant,
        }
        final_status = "finished" if failed == 0 else "finished_with_failures"
        self.repo.update_run(run_id, final_status, metrics)
        self.repo.add_event(
            StepEvent(
                run_id=run_id,
                case_id="_run",
                step_idx=1000,
                event_type="run_finished",
                status=final_status,
                payload=metrics,
            )
        )
