"""Test ArchitectureChecker for domain purity and layer boundaries"""
import types
import tempfile
import os
from pathlib import Path
from app.guardrails import arch_check

def make_py_file(tmp_path, rel_path, content):
    file_path = tmp_path / rel_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    return file_path

def test_domain_purity_detects_forbidden(tmp_path):
    # Create a domain file importing fastapi
    make_py_file(tmp_path, 'domain/foo.py', 'import fastapi\n')
    checker = arch_check.ArchitectureChecker(tmp_path)
    checker._check_domain_purity()
    assert checker.violations
    assert 'fastapi' in checker.violations[0]['error']

def test_layer_boundary_detects_violation(tmp_path):
    # Create application file importing from domain and contracts (contracts not allowed)
    make_py_file(tmp_path, 'application/bar.py', 'from app.domain import foo\nfrom app.contracts import x\n')
    checker = arch_check.ArchitectureChecker(tmp_path)
    checker._check_layer_boundaries()
    found = any('contracts' in v['error'] for v in checker.violations)
    assert found

def test_extract_imports_handles_syntax_error(tmp_path):
    # Create a file with syntax error
    make_py_file(tmp_path, 'domain/bad.py', 'def broken:')
    checker = arch_check.ArchitectureChecker(tmp_path)
    out = checker._extract_imports(tmp_path / 'domain/bad.py')
    assert out == set()

def test_main_success(monkeypatch, tmp_path):
    # Create a valid structure
    (tmp_path / 'domain').mkdir()
    (tmp_path / 'application').mkdir()
    monkeypatch.setattr(arch_check, 'Path', lambda *a, **k: tmp_path)
    monkeypatch.setattr(arch_check, 'ArchitectureChecker', lambda app_path: types.SimpleNamespace(check=lambda: True, print_violations=lambda: None))
    assert arch_check.main() == 0

def test_main_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(arch_check, 'Path', lambda *a, **k: tmp_path)
    monkeypatch.setattr(arch_check, 'ArchitectureChecker', lambda app_path: types.SimpleNamespace(check=lambda: False, print_violations=lambda: None))
    assert arch_check.main() == 1
