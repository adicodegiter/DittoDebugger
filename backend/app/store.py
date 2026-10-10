from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


class LocalRepository:
    """Stores only baseline summaries and explicit experiment outcome records."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS baselines ("
                "id TEXT PRIMARY KEY, captured_at TEXT NOT NULL, graph_version TEXT NOT NULL, "
                "telemetry_status TEXT NOT NULL, telemetry_json TEXT NOT NULL)"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS experiment_outcomes ("
                "id TEXT PRIMARY KEY, target TEXT NOT NULL, action TEXT NOT NULL, outcome TEXT NOT NULL, "
                "evidence_ref TEXT NOT NULL, recorded_at TEXT NOT NULL)"
            )

    def save_baseline(self, graph_version: str, telemetry: dict[str, Any]) -> dict[str, Any]:
        if telemetry.get("status") != "available":
            raise ValueError("A baseline requires fresh, healthy telemetry for all scraped targets.")
        baseline = {
            "baseline_id": f"baseline-{uuid.uuid4().hex[:12]}",
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "graph_version": graph_version,
            "telemetry_status": telemetry["status"],
            "telemetry": telemetry,
        }
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO baselines (id, captured_at, graph_version, telemetry_status, telemetry_json) VALUES (?, ?, ?, ?, ?)",
                (baseline["baseline_id"], baseline["captured_at"], graph_version, telemetry["status"], json.dumps(telemetry)),
            )
        return baseline

    def get_baseline(self, baseline_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, captured_at, graph_version, telemetry_status, telemetry_json FROM baselines WHERE id = ?",
                (baseline_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "baseline_id": row[0],
            "captured_at": row[1],
            "graph_version": row[2],
            "telemetry_status": row[3],
            "telemetry": json.loads(row[4]),
        }

    def record_outcome(self, target: str, action: str, outcome: str, evidence_ref: str) -> None:
        if outcome not in {"failure_observed", "no_failure_observed"}:
            raise ValueError("Only completed, conclusive outcomes can update planner history.")
        if not evidence_ref.strip():
            raise ValueError("An evidence reference is required to record an outcome.")
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO experiment_outcomes (id, target, action, outcome, evidence_ref, recorded_at) VALUES (?, ?, ?, ?, ?, ?)",
                (uuid.uuid4().hex, target, action, outcome, evidence_ref, datetime.now(timezone.utc).isoformat()),
            )

    def history_for(self, target: str, action: str) -> dict[str, int]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT outcome, COUNT(*) FROM experiment_outcomes WHERE target = ? AND action = ? GROUP BY outcome",
                (target, action),
            ).fetchall()
        counts = {outcome: count for outcome, count in rows}
        return {
            "trials": sum(counts.values()),
            "failures": counts.get("failure_observed", 0),
            "non_failures": counts.get("no_failure_observed", 0),
        }

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=2.0)
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()