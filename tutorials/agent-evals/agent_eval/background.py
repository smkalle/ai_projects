from __future__ import annotations

from dataclasses import replace
import threading

from .config import AgentProfile, EvalConfig
from .models import StepEvent
from .runner import EvalRunner


class BackgroundRunManager:
    def __init__(self, runner: EvalRunner):
        self.runner = runner
        self._lock = threading.Lock()
        self._threads: dict[str, threading.Thread] = {}

    def start(self, profile: AgentProfile, config: EvalConfig, only_case_ids: list[str] | None = None) -> str:
        run_id = self.runner.create_run(replace(profile), replace(config))
        thread = threading.Thread(
            target=self._execute,
            args=(run_id, replace(profile), replace(config), list(only_case_ids or [])),
            daemon=True,
            name=f"eval-run-{run_id}",
        )
        with self._lock:
            self._threads[run_id] = thread
        thread.start()
        return run_id

    def is_active(self, run_id: str) -> bool:
        with self._lock:
            thread = self._threads.get(run_id)
        return bool(thread and thread.is_alive())

    def _execute(
        self,
        run_id: str,
        profile: AgentProfile,
        config: EvalConfig,
        only_case_ids: list[str],
    ) -> None:
        try:
            self.runner.execute_run(run_id, profile, config, only_case_ids=only_case_ids or None)
        except Exception as exc:
            self.runner.repo.update_run(run_id, "failed", {"error": str(exc)})
            self.runner.repo.add_event(
                StepEvent(
                    run_id=run_id,
                    case_id="_run",
                    step_idx=1000,
                    event_type="run_failed",
                    status="failed",
                    payload={"error": str(exc)},
                )
            )
        finally:
            with self._lock:
                self._threads.pop(run_id, None)
