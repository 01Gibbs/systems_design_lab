import pytest
from app.application.simulator.scenarios.stale_read import StaleRead

class DummyCounter:
    def __init__(self):
        self.count = 0
        self.labels_args = None
    def labels(self, **kwargs):
        self.labels_args = kwargs
        return self
    def inc(self):
        self.count += 1

@pytest.mark.parametrize("stale_probability,is_stale_expected", [
    (1.0, True),
    (0.0, False),
])
def test_stale_read_metric(stale_probability, is_stale_expected, monkeypatch):
    scenario = StaleRead()
    # Patch random.random to deterministic
    monkeypatch.setattr("random.random", lambda: 0.5)
    metrics = {
        "stale_read_total": DummyCounter(),
        "fresh_read_total": DummyCounter(),
    }
    ctx = {"metrics": metrics}
    params = {"stale_probability": stale_probability, "cache_key_pattern": "foo*"}
    result = scenario.apply(ctx=ctx, parameters=params)
    if is_stale_expected:
        assert metrics["stale_read_total"].count == 1
        assert metrics["fresh_read_total"].count == 0
        assert result["is_stale"] is True
    else:
        assert metrics["stale_read_total"].count == 0
        assert metrics["fresh_read_total"].count == 1
        assert result["is_stale"] is False
