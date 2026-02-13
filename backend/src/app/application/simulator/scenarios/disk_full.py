"""Disk Full Scenario - Simulates disk space exhaustion (write failures)"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.application.simulator.models import ScenarioMeta


@dataclass(frozen=True)
class DiskFull:
    """Simulates disk full condition by causing write failures"""

    meta = ScenarioMeta(
        name="disk-full",
        description="Simulates disk full: causes write operations to fail.",
        targets=["db"],
        parameter_schema={
            "type": "object",
            "properties": {
                "failure_probability": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Probability of disk write failure",
                },
                "path_prefix": {"type": "string"},
            },
            "required": ["failure_probability"],
        },
        safety_limits={},
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        return target.get("category") == "db"

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        failure_probability = float(str(parameters["failure_probability"]))
        path_prefix = str(parameters.get("path_prefix", ""))
        should_fail = random.random() < failure_probability
        if should_fail:
            return {"disk_full_error": True, "path_prefix": path_prefix}
        return {}
