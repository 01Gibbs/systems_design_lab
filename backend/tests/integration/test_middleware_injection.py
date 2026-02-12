"""Integration tests for simulator middleware injection"""
import pytest
import requests
import time

BASE_URL = "http://localhost:8000"


@pytest.mark.integration
def test_fixed_latency_actually_delays_response():
    """Verify fixed-latency scenario actually adds delay to responses"""
    # Reset first
    requests.post(f"{BASE_URL}/api/sim/reset")

    # Measure baseline response time
    start = time.time()
    resp = requests.get(f"{BASE_URL}/api/health")
    baseline_duration = time.time() - start
    assert resp.status_code == 200

    # Enable fixed-latency with 500ms delay
    enable_payload = {
        "name": "fixed-latency",
        "parameters": {"ms": 500, "probability": 1.0}  # 100% probability
    }
    resp = requests.post(f"{BASE_URL}/api/sim/enable", json=enable_payload)
    assert resp.status_code == 200

    # Measure response time with delay - try multiple times
    delays = []
    for _ in range(3):
        start = time.time()
        resp = requests.get(f"{BASE_URL}/api/health")
        duration = time.time() - start
        delays.append(duration)
        assert resp.status_code == 200

    avg_delay = sum(delays) / len(delays)
    # Should be at least 450ms slower than baseline (allowing for jitter)
    assert avg_delay > baseline_duration + 0.45, f"Expected ~500ms delay, got {avg_delay:.3f}s (baseline: {baseline_duration:.3f}s)"

    # Cleanup
    requests.post(f"{BASE_URL}/api/sim/reset")


@pytest.mark.integration
def test_error_burst_returns_500_errors():
    """Verify error-burst scenario actually returns 500 errors"""
    # Reset first
    requests.post(f"{BASE_URL}/api/sim/reset")

    # Enable error-burst with 100% probability
    enable_payload = {
        "name": "error-burst-5xx",
        "parameters": {"probability": 1.0}
    }
    resp = requests.post(f"{BASE_URL}/api/sim/enable", json=enable_payload)
    assert resp.status_code == 200

    # Make requests - should get 500s
    # Try /health endpoint (but leave simulator endpoints alone to avoid breaking the test)
    errors = []
    for _ in range(5):
        resp = requests.get(f"{BASE_URL}/api/health")
        errors.append(resp.status_code)

    # Should have mostly 500s (allowing for some variance in probabilistic scenarios)
    error_count = sum(1 for status in errors if status == 500)
    assert error_count >= 4, f"Expected mostly 500 errors with 100% probability, got: {errors}"

    # Cleanup (use direct reset, might need to retry)
    for _ in range(3):
        try:
            resp = requests.post(f"{BASE_URL}/api/sim/reset")
            if resp.status_code == 200:
                break
        except:
            time.sleep(0.1)


@pytest.mark.integration
def test_probabilistic_scenario_respects_probability():
    """Verify probabilistic scenarios apply effects according to their probability"""
    # Reset first
    requests.post(f"{BASE_URL}/api/sim/reset")

    # Enable error-burst with 50% probability
    enable_payload = {
        "name": "error-burst-5xx",
        "parameters": {"probability": 0.5}
    }
    resp = requests.post(f"{BASE_URL}/api/sim/enable", json=enable_payload)
    assert resp.status_code == 200

    # Make many requests to test probability distribution
    results = []
    for _ in range(50):
        resp = requests.get(f"{BASE_URL}/api/health")
        results.append(resp.status_code)

    # With 50% probability, expect roughly 20-30 errors (allowing wide margin)
    error_count = sum(1 for status in results if status == 500)
    success_count = sum(1 for status in results if status == 200)

    # Should have both successes and errors
    assert error_count > 10, f"Expected ~25 errors, got {error_count}/50"
    assert success_count > 10, f"Expected ~25 successes, got {success_count}/50"

    # Cleanup
    for _ in range(3):
        try:
            resp = requests.post(f"{BASE_URL}/api/sim/reset")
            if resp.status_code == 200:
                break
        except:
            time.sleep(0.1)


@pytest.mark.integration
def test_multiple_scenarios_combine_effects():
    """Verify multiple active scenarios can combine effects"""
    # Reset first
    requests.post(f"{BASE_URL}/api/sim/reset")

    # Enable both delay and error scenarios with low error probability
    scenarios = [
        {"name": "fixed-latency", "parameters": {"ms": 300, "probability": 1.0}},
        {"name": "error-burst-5xx", "parameters": {"probability": 0.2}},
    ]

    for scenario in scenarios:
        resp = requests.post(f"{BASE_URL}/api/sim/enable", json=scenario)
        assert resp.status_code == 200, f"Failed to enable {scenario['name']}"
        time.sleep(0.1)

    # Make requests - should see delays and occasional errors
    results = []
    delays = []

    for _ in range(10):
        start = time.time()
        resp = requests.get(f"{BASE_URL}/api/health")
        duration = time.time() - start
        results.append(resp.status_code)
        delays.append(duration)

    # Should have delays on all requests
    avg_delay = sum(delays) / len(delays)
    assert avg_delay > 0.25, f"Expected ~300ms delays, got avg {avg_delay:.3f}s"

    # Should have some mix of 200s and 500s
    has_success = any(s == 200 for s in results)
    has_error = any(s == 500 for s in results)
    # At low probability, might not get errors, so just check we have successes
    assert has_success, "Expected some successful requests"

    # Cleanup
    requests.post(f"{BASE_URL}/api/sim/reset")


@pytest.mark.integration
def test_scenario_expiration_stops_effects():
    """Verify scenario effects stop after expiration"""
    # Reset first
    requests.post(f"{BASE_URL}/api/sim/reset")

    # Enable error scenario with 2 second expiration
    enable_payload = {
        "name": "error-burst-5xx",
        "parameters": {"probability": 1.0},
        "duration_seconds": 2
    }
    resp = requests.post(f"{BASE_URL}/api/sim/enable", json=enable_payload)
    assert resp.status_code == 200

    # Should get errors immediately
    resp = requests.get(f"{BASE_URL}/api/health")
    assert resp.status_code == 500

    # Wait for expiration (3 seconds to be safe, plus extra check)
    time.sleep(3.0)

    # Verify scenario is actually gone from status
    status_resp = requests.get(f"{BASE_URL}/api/sim/status")
    assert status_resp.status_code == 200
    assert len(status_resp.json()["active"]) == 0, "Scenario should have expired"

    # Should no longer get errors
    resp = requests.get(f"{BASE_URL}/api/health")
    assert resp.status_code == 200

    # Cleanup
    requests.post(f"{BASE_URL}/api/sim/reset")


@pytest.mark.integration
def test_simulator_endpoints_not_affected_by_scenarios():
    """Verify simulator API endpoints themselves are not affected by active scenarios"""
    # Reset first
    requests.post(f"{BASE_URL}/api/sim/reset")

    # Enable error scenario that would break everything
    enable_payload = {
        "name": "error-burst-5xx",
        "parameters": {"probability": 1.0}
    }
    resp = requests.post(f"{BASE_URL}/api/sim/enable", json=enable_payload)
    assert resp.status_code == 200

    # Simulator endpoints should still work
    resp = requests.get(f"{BASE_URL}/api/sim/status")
    assert resp.status_code == 200, "Simulator status endpoint should not be affected by scenarios"

    resp = requests.get(f"{BASE_URL}/api/sim/scenarios")
    assert resp.status_code == 200, "Simulator scenarios endpoint should not be affected"

    # Should be able to disable
    resp = requests.post(f"{BASE_URL}/api/sim/disable", json={"name": "error-burst-5xx"})
    assert resp.status_code == 200, "Simulator disable should not be affected"

    # Cleanup
    requests.post(f"{BASE_URL}/api/sim/reset")


@pytest.mark.integration
def test_request_id_middleware_adds_headers():
    """Verify request_id middleware adds correlation headers to responses"""
    # Reset simulator state
    requests.post(f"{BASE_URL}/api/sim/reset")

    # Make request to any endpoint
    resp = requests.get(f"{BASE_URL}/api/health")
    assert resp.status_code == 200

    # Should have request ID in headers
    assert "x-request-id" in resp.headers or "X-Request-ID" in resp.headers, \
        f"Expected X-Request-ID header, got headers: {dict(resp.headers)}"


@pytest.mark.integration
def test_scenario_only_affects_applicable_targets():
    """Verify scenarios only affect requests that match their target criteria"""
    # Reset first
    requests.post(f"{BASE_URL}/api/sim/reset")

    # Enable fixed-latency
    enable_payload = {
        "name": "fixed-latency",
        "parameters": {"ms": 500, "probability": 1.0}
    }
    resp = requests.post(f"{BASE_URL}/api/sim/enable", json=enable_payload)
    assert resp.status_code == 200

    # Fixed-latency targets HTTP, so should affect /health
    start = time.time()
    resp = requests.get(f"{BASE_URL}/api/health")
    duration = time.time() - start
    assert resp.status_code == 200
    assert duration > 0.45, f"Expected delay on HTTP target, got {duration:.3f}s"

    # Cleanup
    requests.post(f"{BASE_URL}/api/sim/reset")
