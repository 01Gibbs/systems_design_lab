"""Slow DB Query Scenario"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.application.simulator.models import ScenarioMeta


@dataclass(frozen=True)
class SlowDbQuery:
    """Adds deliberate DB delay using pg_sleep"""

    meta = ScenarioMeta(
        name="slow-db-query",
        description="Adds deliberate DB delay using pg_sleep(seconds) in a controlled code path.",
        targets=["db"],
        parameter_schema={
            "type": "object",
            "properties": {
                "seconds": {"type": "number", "minimum": 0.01, "maximum": 5.0},
                "probability": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            },
            "required": ["seconds"],
        },
        safety_limits={"max_seconds": 5.0},
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        return target.get("category") == "db"

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        """Returns effect dict - NO side effects here"""
        prob = parameters.get("probability", 1.0)
        p = float(prob) if isinstance(prob, (int, float, str)) else 1.0
        if random.random() > p:
            return {}

        seconds = parameters["seconds"]
        return {
            "db_sleep_seconds": float(seconds) if isinstance(seconds, (int, float, str)) else 0.01,
        }
