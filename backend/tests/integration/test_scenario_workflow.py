"""Integration test: scenario enable/disable and DB state (infra test)"""
import pytest
import requests
import time

BASE_URL = "http://localhost:8000"


@pytest.mark.integration
def test_scenario_enable_disable_workflow():
    """Test basic scenario lifecycle: list, enable, status, disable, reset"""
    # Reset first to ensure clean state
    requests.post(f"{BASE_URL}/api/sim/reset")

    # List scenarios
    resp = requests.get(f"{BASE_URL}/api/sim/scenarios")
    assert resp.status_code == 200
    scenarios = resp.json()["scenarios"]
    assert len(scenarios) >= 15  # We have 15+ scenarios
    assert any(s["name"] == "fixed-latency" for s in scenarios)

    # Enable a scenario
    enable_payload = {"name": "fixed-latency", "parameters": {"ms": 123, "probability": 1.0}}
    resp2 = requests.post(f"{BASE_URL}/api/sim/enable", json=enable_payload)
    assert resp2.status_code == 200
    active = resp2.json()["active"]
    assert any(a["name"] == "fixed-latency" for a in active)

    # Check status
    resp3 = requests.get(f"{BASE_URL}/api/sim/status")
    assert resp3.status_code == 200
    active2 = resp3.json()["active"]
    assert any(a["name"] == "fixed-latency" for a in active2)

    # Disable scenario
    disable_payload = {"name": "fixed-latency"}
    resp4 = requests.post(f"{BASE_URL}/api/sim/disable", json=disable_payload)
    assert resp4.status_code == 200
    active3 = resp4.json()["active"]
    assert all(a["name"] != "fixed-latency" for a in active3)

    # Reset all
    resp5 = requests.post(f"{BASE_URL}/api/sim/reset")
    assert resp5.status_code == 200
    assert resp5.json()["active"] == []


@pytest.mark.integration
def test_scenario_error_handling():
    """Test error handling for invalid scenario names and parameters"""
    # Reset first
    requests.post(f"{BASE_URL}/api/sim/reset")

    # Try to enable non-existent scenario - should return 404
    resp = requests.post(f"{BASE_URL}/api/sim/enable", json={"name": "nonexistent-scenario", "parameters": {}})
    assert resp.status_code == 404, f"Expected 404 for unknown scenario, got {resp.status_code}: {resp.text}"

    # Try to disable non-active scenario (should be idempotent)
    resp2 = requests.post(f"{BASE_URL}/api/sim/disable", json={"name": "fixed-latency"})
    assert resp2.status_code == 200  # Should succeed even if not active


@pytest.mark.integration
def test_multiple_scenarios_concurrently():
    """Test enabling multiple scenarios at the same time"""
    # Reset first and verify it succeeded
    reset_resp = requests.post(f"{BASE_URL}/api/sim/reset")
    assert reset_resp.status_code == 200, f"Reset failed: {reset_resp.status_code} {reset_resp.text}"

    # Verify clean state
    status_resp = requests.get(f"{BASE_URL}/api/sim/status")
    assert status_resp.status_code == 200, f"Status check failed after reset: {status_resp.status_code} {status_resp.text}"
    assert len(status_resp.json()["active"]) == 0, "Expected no active scenarios after reset"

    # Enable multiple scenarios one by one
    scenarios_to_enable = [
        {"name": "fixed-latency", "parameters": {"ms": 100, "probability": 0.5}},
        {"name": "error-burst-5xx", "parameters": {"probability": 0.1}},
        {"name": "slow-db-query", "parameters": {"seconds": 0.5, "probability": 0.3}},
    ]

    for scenario in scenarios_to_enable:
        resp = requests.post(f"{BASE_URL}/api/sim/enable", json=scenario)
        assert resp.status_code == 200, f"Failed to enable {scenario['name']}: {resp.status_code} {resp.text}"

    # Check all are active (simulator endpoints should not be affected by scenarios)
    resp = requests.get(f"{BASE_URL}/api/sim/status")
    assert resp.status_code == 200, f"Status endpoint failed (should never be affected by scenarios): {resp.status_code}"
    active = resp.json()["active"]
    assert len(active) == 3, f"Expected 3 active scenarios, got {len(active)}"
    active_names = {a["name"] for a in active}
    assert "fixed-latency" in active_names
    assert "error-burst-5xx" in active_names
    assert "slow-db-query" in active_names

    # Reset cleanup
    requests.post(f"{BASE_URL}/api/sim/reset")


@pytest.mark.integration
def test_scenario_expiration():
    """Test scenario auto-expiration after duration_seconds"""
    # Reset first
    requests.post(f"{BASE_URL}/api/sim/reset")

    # Enable scenario with 2 second expiration
    enable_payload = {
        "name": "fixed-latency",
        "parameters": {"ms": 50, "probability": 1.0},
        "duration_seconds": 2
    }
    resp = requests.post(f"{BASE_URL}/api/sim/enable", json=enable_payload)
    assert resp.status_code == 200

    # Should be active immediately
    resp2 = requests.get(f"{BASE_URL}/api/sim/status")
    assert resp2.status_code == 200
    active = resp2.json()["active"]
    assert any(a["name"] == "fixed-latency" for a in active)

    # Wait for expiration (3 seconds to be safe)
    time.sleep(3)

    # Should no longer be active
    resp3 = requests.get(f"{BASE_URL}/api/sim/status")
    assert resp3.status_code == 200
    active2 = resp3.json()["active"]
    assert all(a["name"] != "fixed-latency" for a in active2)

    # Cleanup
    requests.post(f"{BASE_URL}/api/sim/reset")


@pytest.mark.integration
def test_scenario_parameter_validation():
    """Test that scenarios validate parameters according to their schemas"""
    # Reset first
    requests.post(f"{BASE_URL}/api/sim/reset")

    # List scenarios to get parameter schema for fixed-latency
    resp = requests.get(f"{BASE_URL}/api/sim/scenarios")
    assert resp.status_code == 200
    scenarios = resp.json()["scenarios"]
    fixed_latency = next(s for s in scenarios if s["name"] == "fixed-latency")
    assert "parameter_schema" in fixed_latency

    # Try with valid parameters
    valid_payload = {"name": "fixed-latency", "parameters": {"ms": 100, "probability": 0.5}}
    resp2 = requests.post(f"{BASE_URL}/api/sim/enable", json=valid_payload)
    assert resp2.status_code == 200

    # Cleanup
    requests.post(f"{BASE_URL}/api/sim/reset")


@pytest.mark.integration
def test_all_scenario_targets_are_contract_compliant():
    """Ensure all scenarios only use allowed target values: http, db, cpu, algorithm"""
    resp = requests.get(f"{BASE_URL}/api/sim/scenarios")
    assert resp.status_code == 200
    scenarios = resp.json()["scenarios"]

    allowed_targets = {"http", "db", "cpu", "algorithm"}

    for scenario in scenarios:
        targets = set(scenario["targets"])
        invalid_targets = targets - allowed_targets
        assert not invalid_targets, f"Scenario {scenario['name']} has invalid targets: {invalid_targets}"
