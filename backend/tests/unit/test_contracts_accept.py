"""Test contracts_accept accept_contracts logic (mocked)"""
import types
import sys
from app.guardrails import contracts_accept

def test_accept_contracts_success(monkeypatch, tmp_path):
    # Create backend directory structure
    backend_root = tmp_path / "backend" / "src" / "app" / "guardrails"
    backend_root.mkdir(parents=True)
    
    # Patch app.api.main.app.openapi to return a dict
    fake_app = types.SimpleNamespace(openapi=lambda: {"openapi": "3.0.0"})
    monkeypatch.setitem(sys.modules, 'app.api.main', types.SimpleNamespace(app=fake_app))
    
    # Patch __file__ to point to the test backend structure
    # Path(__file__).parent.parent.parent.parent = backend root
    # backend_root.parent = project root
    test_file = backend_root / "contracts_accept.py"
    test_file.touch()
    monkeypatch.setattr(contracts_accept, '__file__', str(test_file))
    
    # Run accept_contracts - it should write to tmp_path/openapi.json (project root)
    result = contracts_accept.accept_contracts()
    assert result == 0
    assert (tmp_path / 'openapi.json').exists()

def test_accept_contracts_failure(monkeypatch):
    monkeypatch.setattr(contracts_accept, 'Path', lambda *a, **k: 1/0)  # force error
    import pytest
    with pytest.raises(ZeroDivisionError):
        contracts_accept.accept_contracts()
