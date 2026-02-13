"""Custom exceptions for simulator operations"""

from __future__ import annotations


class SimulatorError(Exception):
    """Base exception for simulator-related errors"""

    pass


class ScenarioNotFoundError(SimulatorError):
    """Raised when a scenario name is not recognized"""

    def __init__(self, scenario_name: str):
        self.scenario_name = scenario_name
        super().__init__(f"Scenario '{scenario_name}' not found")


class InvalidParametersError(SimulatorError):
    """Raised when scenario parameters are invalid"""

    def __init__(self, scenario_name: str, message: str):
        self.scenario_name = scenario_name
        super().__init__(f"Invalid parameters for scenario '{scenario_name}': {message}")
