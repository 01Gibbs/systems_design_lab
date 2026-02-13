"""Scenario Template - Copy this file to create new scenarios

This template demonstrates:
- Required structure and imports
- Parameter schema patterns
- Safety limits
- Probabilistic behavior
- Effect-based return values (NO SIDE EFFECTS)
- Target filtering

Steps to create a new scenario:
1. Copy this file to a new name (e.g., rate_limit.py)
2. Update class name, meta fields, and docstrings
3. Implement is_applicable() to filter targets
4. Implement apply() to return effect dict
5. Add to registry in registry.py
6. Write unit tests in tests/unit/test_simulator_scenarios.py
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from app.application.simulator.models import ScenarioMeta


@dataclass(frozen=True)
class TemplateScenario:
    """
    One-line description of what this scenario simulates.

    Detailed description of:
    - What real-world issue this represents
    - When you might encounter this in production
    - How it affects systems
    - Example use case for learning
    """

    meta = ScenarioMeta(
        name="template-scenario",  # kebab-case, unique identifier
        description="Brief description shown in API/UI. Keep under 100 chars.",
        targets=["http"],  # List of categories: "http", "db", "cache", "algorithm"
        parameter_schema={
            # JSON Schema format - used for validation and UI generation
            "type": "object",
            "properties": {
                # Required parameter example
                "delay_ms": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5000,
                    "description": "Delay duration in milliseconds",
                },
                # Optional string parameter
                "path_prefix": {
                    "type": "string",
                    "description": "Only apply to routes starting with this prefix",
                },
                # Optional enum parameter
                "severity": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Severity level of the effect",
                },
                # Probability parameter (common pattern)
                "probability": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Probability of effect occurring (0.0-1.0)",
                },
            },
            "required": ["delay_ms"],  # List required parameters
        },
        safety_limits={
            # Document maximum safe values to prevent system damage
            "max_delay_ms": 5000,
            "max_probability": 1.0,
        },
    )

    def is_applicable(self, *, target: dict[str, str]) -> bool:
        """
        Check if this scenario applies to the given target.

        Args:
            target: Dict with "category" key ("http", "db", "cache", "algorithm")

        Returns:
            True if scenario should be evaluated for this target

        Common patterns:
        - HTTP scenarios: target.get("category") == "http"
        - DB scenarios: target.get("category") == "db"
        - Cache scenarios: target.get("category") == "cache"
        - Algorithm scenarios: target.get("category") == "algorithm"
        - Multi-target: target.get("category") in ["http", "db"]
        """
        return target.get("category") == "http"

    def apply(self, *, ctx: dict[str, object], parameters: dict[str, object]) -> dict[str, object]:
        """
        Return effect dictionary for middleware/adapters to apply.

        CRITICAL: This method MUST NOT have side effects. It should only:
        - Read from ctx and parameters
        - Make probabilistic decisions
        - Return a dict describing what effects to apply

        Args:
            ctx: Context dict with request info (method, path, etc.)
            parameters: User-provided parameters from enable scenario request

        Returns:
            Dict of effects for middleware/adapters to apply. Empty dict = no effect.

        Common effect keys:
        - http_delay_ms: Add HTTP response delay
        - http_force_error: Force 500 error
        - http_path_prefix: Only apply to matching paths
        - http_method: Only apply to matching methods
        - db_sleep_seconds: Add DB query delay
        - cache_invalidate: Force cache miss
        - algorithm_use_slow: Use slow algorithm path

        Patterns:
        1. Probabilistic behavior:
           if random.random() > probability:
               return {}

        2. Parameter validation:
           delay = int(parameters["delay_ms"])
           if delay > 5000:
               delay = 5000  # Enforce safety limit

        3. Contextual filtering:
           if ctx.get("path", "").startswith("/admin"):
               return {}  # Skip admin routes

        4. Always include scenario name for tracking:
           return {"effect_key": value, "scenario_name": self.meta.name}
        """

        # Example: Probabilistic behavior
        prob = parameters.get("probability", 1.0)
        p = float(prob) if isinstance(prob, (int, float, str)) else 1.0
        if random.random() > p:
            return {}  # No effect this time

        # Example: Extract and validate parameters
        delay_ms = parameters.get("delay_ms", 0)
        delay = int(delay_ms) if isinstance(delay_ms, (int, str)) else 0

        # Example: Enforce safety limits
        if delay > 5000:
            delay = 5000

        # Example: Build effect dict
        effects = {
            "http_delay_ms": delay,
            "http_path_prefix": str(parameters.get("path_prefix", "")),
            "scenario_name": self.meta.name,
        }

        # Optional: Add conditional effects
        severity = parameters.get("severity", "low")
        if severity == "high":
            effects["http_force_error"] = True

        return effects


# ==============================================================================
# TEST TEMPLATE - Copy this to tests/unit/test_simulator_scenarios.py
# ==============================================================================
"""
from app.application.simulator.scenarios.template_scenario import TemplateScenario


def test_template_scenario_apply_and_applicable(monkeypatch):
    '''Test TemplateScenario behavior'''
    ts = TemplateScenario()

    # Test applicability
    assert ts.is_applicable(target={"category": "http"})
    assert not ts.is_applicable(target={"category": "db"})

    # Test basic effect generation
    monkeypatch.setattr("random.random", lambda: 0.0)  # Force probability
    result = ts.apply(
        ctx={},
        parameters={"delay_ms": 1000, "probability": 1.0}
    )
    assert result["http_delay_ms"] == 1000
    assert result["scenario_name"] == "template-scenario"

    # Test no effect when probability not met
    monkeypatch.setattr("random.random", lambda: 1.0)  # Avoid effect
    result = ts.apply(
        ctx={},
        parameters={"delay_ms": 1000, "probability": 0.0}
    )
    assert result == {}

    # Test safety limits
    monkeypatch.setattr("random.random", lambda: 0.0)
    result = ts.apply(
        ctx={},
        parameters={"delay_ms": 99999}  # Over safety limit
    )
    assert result["http_delay_ms"] == 5000  # Capped


def test_template_scenario_metadata():
    '''Test scenario metadata is complete'''
    ts = TemplateScenario()
    assert ts.meta.name == "template-scenario"
    assert ts.meta.description != ""
    assert "http" in ts.meta.targets
    assert "delay_ms" in ts.meta.parameter_schema["properties"]
    assert "required" in ts.meta.parameter_schema
"""

# ==============================================================================
# REGISTRY TEMPLATE - Add this to registry.py build_registry() function
# ==============================================================================
"""
from app.application.simulator.scenarios.template_scenario import TemplateScenario

def build_registry() -> ScenarioRegistry:
    items: list[Scenario] = [
        # ... existing scenarios ...
        TemplateScenario(),  # Add new scenario here
    ]
    return ScenarioRegistry({s.meta.name: s for s in items})
"""
