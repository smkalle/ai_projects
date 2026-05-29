from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import CaseResult, EvalRun, StepEvent


class EvalRepository:
    def __init__(self, db_path: str = "./eval_runs.db"):
        self.db_path = Path(db_path)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    dataset_id TEXT NOT NULL,
                    agent_profile TEXT NOT NULL,
                    eval_config TEXT NOT NULL,
                    git_sha TEXT NOT NULL,
                    metrics_summary TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS step_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    case_id TEXT NOT NULL,
                    step_idx INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    duration_ms INTEGER NOT NULL,
                    timestamp TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS case_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    case_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    score REAL NOT NULL,
                    latency_ms INTEGER NOT NULL,
                    answer TEXT NOT NULL,
                    assertions TEXT NOT NULL
                );
                """
            )

    def create_run(self, run: EvalRun) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO runs(run_id, created_at, status, dataset_id, agent_profile, eval_config, git_sha, metrics_summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.created_at,
                    run.status,
                    run.dataset_id,
                    json.dumps(run.agent_profile),
                    json.dumps(run.eval_config),
                    run.git_sha,
                    json.dumps(run.metrics_summary),
                ),
            )

    def update_run(self, run_id: str, status: str, metrics_summary: dict[str, Any]) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE runs SET status = ?, metrics_summary = ? WHERE run_id = ?",
                (status, json.dumps(metrics_summary), run_id),
            )

    def add_event(self, event: StepEvent) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO step_events(run_id, case_id, step_idx, event_type, status, payload, duration_ms, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.run_id,
                    event.case_id,
                    event.step_idx,
                    event.event_type,
                    event.status,
                    json.dumps(event.payload),
                    event.duration_ms,
                    event.timestamp,
                ),
            )

    def add_case_result(self, result: CaseResult) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO case_results(run_id, case_id, status, score, latency_ms, answer, assertions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.run_id,
                    result.case_id,
                    result.status,
                    result.score,
                    result.latency_ms,
                    result.answer,
                    json.dumps(result.assertions),
                ),
            )

    def list_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT run_id, created_at, status, dataset_id, metrics_summary FROM runs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) | {"metrics_summary": json.loads(row["metrics_summary"])} for row in rows]

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,)).fetchone()
        if not row:
            return None
        run = dict(row)
        for key in ("agent_profile", "eval_config", "metrics_summary"):
            run[key] = json.loads(run[key])
        return run

    def get_events(self, run_id: str) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM step_events WHERE run_id = ? ORDER BY id ASC",
                (run_id,),
            ).fetchall()
        return [dict(row) | {"payload": json.loads(row["payload"])} for row in rows]

    def get_case_results(self, run_id: str) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM case_results WHERE run_id = ? ORDER BY id ASC",
                (run_id,),
            ).fetchall()
        return [dict(row) | {"assertions": json.loads(row["assertions"])} for row in rows]
