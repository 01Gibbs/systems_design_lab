"""Scenario Registry - Central registration and lookup for scenarios"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from backend.simulator.scenario import Scenario, ScenarioStatus


class ScenarioRegistry:
    """
    Registry for all available scenarios.

    Scenarios are registered at application startup and can be
    enabled/disabled at runtime with specific parameters.
    """

    def __init__(self) -> None:
        self._scenarios: Dict[str, Scenario] = {}
        self._active: Dict[str, ScenarioStatus] = {}

    def register(self, scenario: Scenario) -> None:
        """Register a scenario"""
        if scenario.name in self._scenarios:
            raise ValueError(f"Scenario already registered: {scenario.name}")
        self._scenarios[scenario.name] = scenario

    def get_scenario(self, name: str) -> Optional[Scenario]:
        """Get a scenario by name"""
        return self._scenarios.get(name)

    def list_scenarios(self) -> list[Dict[str, Any]]:
        """List all available scenarios with their metadata"""
        return [
            {
                "name": scenario.name,
                "description": scenario.description,
                "injection_points": [ip.value for ip in scenario.injection_points],
                "targets": [t.value for t in scenario.targets],
                "parameter_schema": scenario.parameter_schema(),
                "safety_limits": scenario.safety_limits(),
            }
            for scenario in self._scenarios.values()
        ]

    def enable_scenario(
        self,
        name: str,
        parameters: Dict[str, Any],
        duration_seconds: Optional[int] = None,
    ) -> None:
        """
        Enable a scenario with given parameters.

        Args:
            name: Scenario name
            parameters: Scenario parameters (will be validated)
            duration_seconds: Optional duration before auto-disable
        """
        scenario = self.get_scenario(name)
        if not scenario:
            raise ValueError(f"Unknown scenario: {name}")

        # Validate parameters
        scenario.validate_parameters(parameters)

        # Calculate expiry
        expires_at = None
        if duration_seconds:
            expires_at = datetime.utcnow() + timedelta(seconds=duration_seconds)

        # Store status
        self._active[name] = ScenarioStatus(
            name=name,
            enabled=True,
            parameters=parameters,
            enabled_at=datetime.utcnow(),
            expires_at=expires_at,
        )

    def disable_scenario(self, name: str) -> None:
        """Disable a scenario"""
        if name in self._active:
            del self._active[name]

    def disable_all(self) -> None:
        """Disable all active scenarios"""
        self._active.clear()

    def get_active_scenarios(self) -> list[ScenarioStatus]:
        """Get all currently active scenarios (non-expired)"""
        # Clean up expired scenarios
        expired = [
            name for name, status in self._active.items() if status.is_expired()
        ]
        for name in expired:
            del self._active[name]

        return list(self._active.values())

    def is_scenario_active(self, name: str) -> bool:
        """Check if a specific scenario is currently active"""
        if name not in self._active:
            return False

        status = self._active[name]
        if status.is_expired():
            del self._active[name]
            return False

        return True

    def get_scenario_parameters(self, name: str) -> Optional[Dict[str, Any]]:
        """Get parameters for an active scenario"""
        if not self.is_scenario_active(name):
            return None
        return self._active[name].parameters


# Global registry instance
registry = ScenarioRegistry()


def get_registry() -> ScenarioRegistry:
    """Get the global scenario registry"""
    return registry
