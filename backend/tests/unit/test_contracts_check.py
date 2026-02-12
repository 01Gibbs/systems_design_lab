"""Test ContractChecker for drift detection and diff printing"""
import types
import sys
from app.guardrails import contracts_check

def test_check_drift_snapshot_missing(tmp_path):
    # tmp_path represents the backend root, checker looks for openapi.json in parent
    backend_root = tmp_path / "backend"
    backend_root.mkdir()
    checker = contracts_check.ContractChecker(backend_root)
    assert not checker.check_drift()
    assert 'No OpenAPI snapshot found' in checker.violations[0]

def test_check_drift_schema_equal(monkeypatch, tmp_path):
    # Write a snapshot at project root (parent of backend/)
    backend_root = tmp_path / "backend"
    backend_root.mkdir()
    snap = {"openapi": "3.0.0"}
    (tmp_path / 'openapi.json').write_text('{"openapi": "3.0.0"}')
    checker = contracts_check.ContractChecker(backend_root)
    monkeypatch.setattr(contracts_check, 'Path', lambda *a, **k: backend_root)
    monkeypatch.setitem(sys.modules, 'app.api.main', types.SimpleNamespace(app=types.SimpleNamespace(openapi=lambda: snap)))
    assert checker.check_drift()
    assert not checker.violations

def test_check_drift_schema_diff(monkeypatch, tmp_path, capsys):
    # Write a snapshot at project root (parent of backend/)
    backend_root = tmp_path / "backend"
    backend_root.mkdir()
    snap = {"openapi": "3.0.0", "paths": {"/foo": {"get": {}}}, "info": {"version": "1.0"}}
    new = {"openapi": "3.0.0", "paths": {"/bar": {"post": {}}}, "info": {"version": "2.0"}}
    (tmp_path / 'openapi.json').write_text('{"openapi": "3.0.0", "paths": {"/foo": {"get": {}}}, "info": {"version": "1.0"}}')
    checker = contracts_check.ContractChecker(backend_root)
    monkeypatch.setattr(contracts_check, 'Path', lambda *a, **k: backend_root)
    monkeypatch.setitem(sys.modules, 'app.api.main', types.SimpleNamespace(app=types.SimpleNamespace(openapi=lambda: new)))
    assert not checker.check_drift()
    out = capsys.readouterr().out
    assert 'Added endpoints' in out or 'Removed endpoints' in out or 'Version' in out

def test_main_success(monkeypatch, tmp_path):
    backend_root = tmp_path / "backend"
    backend_root.mkdir()
    monkeypatch.setattr(contracts_check, 'Path', lambda *a, **k: backend_root)
    monkeypatch.setattr(contracts_check, 'ContractChecker', lambda backend_root: types.SimpleNamespace(check_drift=lambda: True, print_violations=lambda: None))
    assert contracts_check.main() == 0

def test_main_failure(monkeypatch, tmp_path):
    backend_root = tmp_path / "backend"
    backend_root.mkdir()
    monkeypatch.setattr(contracts_check, 'Path', lambda *a, **k: backend_root)
    monkeypatch.setattr(contracts_check, 'ContractChecker', lambda backend_root: types.SimpleNamespace(check_drift=lambda: False, print_violations=lambda: None))
    assert contracts_check.main() == 1
