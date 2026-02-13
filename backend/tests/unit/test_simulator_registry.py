"""Test ScenarioRegistry for registration and lookup"""

import ast
from pathlib import Path

import pytest

from app.application.simulator.models import ScenarioMeta
from app.application.simulator.registry import Scenario, ScenarioRegistry, build_registry

class DummyScenario:
    def __init__(self, name="dummy", desc="desc"):
        self.meta = ScenarioMeta(
            name=name,
            description=desc,
            targets=["http"],
            parameter_schema={},
            safety_limits={},
        )
    def is_applicable(self, *, target):
        return True
    def apply(self, *, ctx, parameters):
        return {"effect": True}

def test_registry_get_and_list():
    s1 = DummyScenario("foo")
    s2 = DummyScenario("bar")
    reg = ScenarioRegistry({s1.meta.name: s1, s2.meta.name: s2})
    # List
    scenarios = reg.scenarios
    assert set(scenarios.keys()) == {"foo", "bar"}
    # Get
    assert reg.get("foo") is s1
    assert reg.get("bar") is s2

def test_registry_get_missing():
    reg = ScenarioRegistry({})
    with pytest.raises(KeyError) as e:
        reg.get("nope")
    assert "Unknown scenario" in str(e.value)


def test_all_scenario_files_are_registered():
    """
    Ensure every scenario file in the scenarios directory is registered.

    This test prevents scenarios from being implemented but forgotten in registry.
    
    It verifies that for each .py file in scenarios/ (excluding __init__.py and TEMPLATE.py),
    there is a corresponding scenario registered in build_registry().
    """
    # Get scenarios directory (from tests/unit -> tests -> backend -> src -> app -> ...)
    test_file_dir = Path(__file__).parent  # tests/unit
    backend_dir = test_file_dir.parent.parent  # backend/
    scenarios_dir = backend_dir / "src" / "app" / "application" / "simulator" / "scenarios"
    
    # List all scenario files
    scenario_files = [
        f.stem for f in scenarios_dir.glob("*.py")
        if f.stem not in ["__init__", "TEMPLATE"] and f.is_file()
    ]
    
    # Build the actual registry
    registry = build_registry()
    registered_names = set(registry.scenarios.keys())
    
    # Verify we have at least the expected number of files
    assert len(scenario_files) >= 15, f"Expected at least 15 scenario files, found {len(scenario_files)}"
    
    # For informational purposes: list what we found
    print(f"\n  Found {len(scenario_files)} scenario files")
    print(f"  Registered {len(registered_names)} scenarios")
    
    # Verify each scenario file has a kebab-case name in the registry
    # We check that each file corresponds to at least one registered scenario
    # by converting file names to kebab-case and checking they exist
    
    file_to_kebab = {
        "fixed_latency": "fixed-latency",
        "error_burst": "error-burst-5xx",
        "slow_db_query": "slow-db-query",
        "lock_contention": "lock-contention",
        "algorithmic_degradation": "algorithmic-degradation",
        "circuit_breaker": "circuit-breaker",
        "retry_storm": "retry-storm",
        "connection_pool_exhaustion": "connection-pool-exhaustion",
        "cache_stampede": "cache-stampede",
        "cpu_spike": "cpu-spike",
        "memory_leak": "memory-leak",
        "disk_full": "disk-full",
        "network_partition": "network-partition",
        "clock_skew": "clock-skew",
        "resource_starvation": "resource-starvation",
    }
    
    missing_registrations = []
    for file_name in scenario_files:
        # Skip if we don't have a mapping (future scenarios)
        if file_name not in file_to_kebab:
            # Try basic conversion: snake_case to kebab-case
            expected_name = file_name.replace("_", "-")
            if expected_name not in registered_names:
                missing_registrations.append(file_name)
        else:
            expected_name = file_to_kebab[file_name]
            if expected_name not in registered_names:
                missing_registrations.append(file_name)
    
    assert not missing_registrations, (
        f"The following scenario files are not registered in build_registry():\n"
        f"  {', '.join(missing_registrations)}\n"
        f"Add them to backend/src/app/application/simulator/registry.py"
    )
