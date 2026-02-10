"""Scenario Interface - Base class for all simulator scenarios"""
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class InjectionPoint(str, Enum):
    """Where the scenario injects behavior"""

    REQUEST = "request"  # HTTP request layer
    RESPONSE = "response"  # HTTP response layer
    DATABASE = "database"  # Database operations
    CACHE = "cache"  # Cache operations
    CPU = "cpu"  # CPU-intensive operations
    ALGORITHM = "algorithm"  # Algorithmic complexity


class ScenarioTarget(str, Enum):
    """What the scenario targets"""

    ALL_ROUTES = "all_routes"
    SPECIFIC_ROUTE = "specific_route"
    SPECIFIC_METHOD = "specific_method"
    DATABASE_QUERIES = "database_queries"
    CACHE_OPERATIONS = "cache_operations"


class ScenarioStatus:
    """Runtime status of a scenario"""

    def __init__(
        self,
        name: str,
        enabled: bool,
        parameters: Dict[str, Any],
        enabled_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
    ):
        self.name = name
        self.enabled = enabled
        self.parameters = parameters
        self.enabled_at = enabled_at
        self.expires_at = expires_at

    def is_expired(self) -> bool:
        """Check if scenario has expired"""
        if not self.enabled or not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "parameters": self.parameters,
            "enabled_at": self.enabled_at.isoformat() if self.enabled_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class Scenario(ABC):
    """
    Base class for all simulator scenarios.

    Each scenario implements a specific failure mode or system issue.
    Scenarios are registered and can be enabled/disabled at runtime.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique, stable scenario name (e.g., 'latency_fixed')"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this scenario does"""
        pass

    @property
    @abstractmethod
    def injection_points(self) -> list[InjectionPoint]:
        """Where this scenario injects its behavior"""
        pass

    @property
    @abstractmethod
    def targets(self) -> list[ScenarioTarget]:
        """What this scenario targets"""
        pass

    @abstractmethod
    def parameter_schema(self) -> Dict[str, Any]:
        """
        JSON schema for scenario parameters.

        Example:
        {
            "type": "object",
            "properties": {
                "latency_ms": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 10000,
                    "description": "Latency to inject in milliseconds"
                }
            },
            "required": ["latency_ms"]
        }
        """
        pass

    @abstractmethod
    def safety_limits(self) -> Dict[str, Any]:
        """
        Safety constraints for this scenario.

        Example:
        {
            "max_duration_seconds": 3600,
            "max_probability": 1.0,
            "max_latency_ms": 10000
        }
        """
        pass

    @abstractmethod
    async def apply(self, context: Dict[str, Any], parameters: Dict[str, Any]) -> None:
        """
        Apply the scenario's effects.

        Args:
            context: Execution context (request, DB connection, etc.)
            parameters: Validated parameters for this scenario
        """
        pass

    def validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Validate parameters against schema and safety limits.

        Raises ValueError if validation fails.
        Override this method for custom validation logic.
        """
        # Basic validation - can be enhanced with jsonschema
        schema = self.parameter_schema()
        required = schema.get("required", [])

        for field in required:
            if field not in parameters:
                raise ValueError(f"Missing required parameter: {field}")

        # Check safety limits
        limits = self.safety_limits()
        for key, max_value in limits.items():
            param_key = key.replace("max_", "")
            if param_key in parameters and parameters[param_key] > max_value:
                raise ValueError(
                    f"Parameter {param_key}={parameters[param_key]} exceeds safety limit {max_value}"
                )
