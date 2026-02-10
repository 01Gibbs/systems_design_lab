"""
Template Scenario - Use this as a starting point for new scenarios

To add a new scenario:
1. Copy this file to a new file in scenarios/
2. Implement all abstract methods
3. Register in backend/main.py or a startup module
4. Add tests in tests/unit/simulator/
"""
from typing import Any, Dict

from backend.simulator.scenario import InjectionPoint, Scenario, ScenarioTarget


class TemplateScenario(Scenario):
    """
    Template scenario demonstrating the interface.

    Replace this docstring with a description of what your scenario does.
    """

    @property
    def name(self) -> str:
        """Unique name for this scenario (use snake_case)"""
        return "template_scenario"

    @property
    def description(self) -> str:
        """User-facing description"""
        return "Template scenario for demonstration purposes"

    @property
    def injection_points(self) -> list[InjectionPoint]:
        """Where this scenario injects behavior"""
        return [InjectionPoint.REQUEST]

    @property
    def targets(self) -> list[ScenarioTarget]:
        """What this scenario targets"""
        return [ScenarioTarget.ALL_ROUTES]

    def parameter_schema(self) -> Dict[str, Any]:
        """
        Define parameters this scenario accepts.

        Return a JSON schema object describing parameters.
        """
        return {
            "type": "object",
            "properties": {
                "example_param": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 1000,
                    "description": "Example parameter in milliseconds",
                }
            },
            "required": ["example_param"],
        }

    def safety_limits(self) -> Dict[str, Any]:
        """
        Define safety constraints.

        Keys should match parameter names with 'max_' prefix.
        """
        return {
            "max_example_param": 1000,
            "max_duration_seconds": 3600,
        }

    async def apply(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> None:
        """
        Apply the scenario's effects.

        This is where you implement the actual behavior.

        Args:
            context: Execution context with request/response/DB objects
            parameters: Validated parameters for this scenario
        """
        # Example: access parameter
        value = parameters["example_param"]

        # Example: modify request/response in context
        if "request" in context:
            # Do something with the request
            pass

        if "response" in context:
            # Do something with the response
            pass

        # Implement your scenario logic here
        pass
