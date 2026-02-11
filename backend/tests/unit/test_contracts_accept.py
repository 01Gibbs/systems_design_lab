"""Test contracts_accept accept_contracts logic (mocked)"""
import types
import sys
from app.guardrails import contracts_accept

def test_accept_contracts_success(monkeypatch, tmp_path):
    # Patch app.api.main.app.openapi to return a dict
    fake_app = types.SimpleNamespace(openapi=lambda: {"openapi": "3.0.0"})
    monkeypatch.setitem(sys.modules, 'app.api.main', types.SimpleNamespace(app=fake_app))
    # Patch Path and open
    monkeypatch.setattr(contracts_accept, 'Path', lambda *a, **k: tmp_path)
    import builtins
    orig_open = builtins.open
    monkeypatch.setattr('builtins.open', lambda *a, **k: orig_open(tmp_path / 'openapi.json', 'w', encoding='utf-8'))
    assert contracts_accept.accept_contracts() == 0
    assert (tmp_path / 'openapi.json').exists()

def test_accept_contracts_failure(monkeypatch):
    monkeypatch.setattr(contracts_accept, 'Path', lambda *a, **k: 1/0)  # force error
    import pytest
    with pytest.raises(ZeroDivisionError):
        contracts_accept.accept_contracts()
