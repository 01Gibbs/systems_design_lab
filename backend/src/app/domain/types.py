"""Domain-level type aliases for type-safe JSON-like structures.

This module eliminates usage of `Any` by providing explicit type aliases
for JSON-like data structures. Domain layer types can be imported by both
application and contracts layers.
"""

# JSON primitive types
JsonPrimitive = str | int | float | bool | None

# JSON object for simple dictionaries (non-recursive for Pydantic compatibility)
# Use dict[str, object] for most cases to avoid recursive type issues with Pydantic
JsonSchema = dict[str, object]

# Parameter values at runtime (more constrained than full JSON)
# Scenarios typically use primitives and simple nested structures
ParameterValue = JsonPrimitive | dict[str, JsonPrimitive] | list[JsonPrimitive]

# Parameter dictionaries (scenario configuration at runtime)
Parameters = dict[str, ParameterValue]
