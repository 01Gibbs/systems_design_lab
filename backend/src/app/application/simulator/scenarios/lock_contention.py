"""Lock Contention Scenario"""

from __future__ import annotations

from dataclasses import dataclass

from app.application.simulator.models import ScenarioMeta


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
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        return target.get("category") == "db"

    def apply(self, *, ctx: dict, parameters: dict) -> dict:
        """Returns effect dict - NO side effects here"""
        return {
            "db_lock_contention": True,
            "db_target_row_id": int(parameters["row_id"]),
            "db_concurrent_updates": int(parameters["update_count"]),
        }
