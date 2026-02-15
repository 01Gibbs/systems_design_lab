"""Lock Contention Scenario"""

from __future__ import annotations

from dataclasses import dataclass

from app.application.simulator.models import MetricSpec, ScenarioMeta


@dataclass(frozen=True)
class LockContention:
    """Simulates lock contention on database rows"""

    meta = ScenarioMeta(
        name="lock-contention",
        description="Concurrent updates on same row to trigger lock contention.",
        targets=["db"],
        parameter_schema={
            "type": "object",
            "properties": {
                "row_id": {"type": "integer", "minimum": 1},
                "update_count": {"type": "integer", "minimum": 2, "maximum": 100},
            },
            "required": ["row_id", "update_count"],
        },
        safety_limits={"max_update_count": 100},
        metrics=[
            MetricSpec(
                name="db_lock_attempts_total",
                type="counter",
                description="Total number of DB lock attempts by scenario",
                labels=["scenario"],
            ),
            MetricSpec(
                name="db_lock_conflicts_total",
                type="counter",
                description="Total number of DB lock conflicts by scenario",
                labels=["scenario"],
            ),
        ],
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        return target.get("category") == "db"

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        """Returns effect dict - NO side effects here"""
        row_id = parameters["row_id"]
        update_count = parameters["update_count"]
        return {
            "db_lock_contention": True,
            "db_target_row_id": int(row_id) if isinstance(row_id, (int, str)) else 0,
            "db_concurrent_updates": (
                int(update_count) if isinstance(update_count, (int, str)) else 0
            ),
        }
