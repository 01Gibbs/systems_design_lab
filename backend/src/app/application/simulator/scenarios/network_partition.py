"""Network Partition Scenario - Simulates partial network loss between services"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.application.simulator.models import ScenarioMeta


@dataclass(frozen=True)
class NetworkPartition:
    """Simulates network partition by dropping or delaying requests"""

    meta = ScenarioMeta(
        name="network-partition",
        description="Simulates network partition: drops or delays requests to certain targets.",
        targets=["http", "database"],
        parameter_schema={
            "type": "object",
            "properties": {
                "partition_probability": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Probability of partition event",
                },
                "delay_ms": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 10000,
                    "description": "Artificial delay for partitioned requests",
                },
                "drop": {
                    "type": "boolean",
                    "description": "Whether to drop requests entirely",
                },
            },
            "required": ["partition_probability"],
        },
        safety_limits={"max_delay_ms": 10000},
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        return target.get("category") in ("http", "database")

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        partition_probability = float(str(parameters["partition_probability"]))
        delay_ms = int(str(parameters.get("delay_ms", 1000)))
        drop = bool(parameters.get("drop", False))
        should_partition = random.random() < partition_probability
        if should_partition:
            effect: dict[str, object] = {"network_partition": True, "delay_ms": delay_ms}
            if drop:
                effect["drop_request"] = True
            return effect
        return {}
