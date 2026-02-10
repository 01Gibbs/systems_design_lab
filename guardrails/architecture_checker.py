"""Architecture Boundary Checker - Enforces Clean Architecture layer rules"""
import ast
import sys
from pathlib import Path
from typing import Dict, List, Set


class ArchitectureChecker:
    """Validates import boundaries between Clean Architecture layers"""

    # Forbidden imports for domain layer (NO framework dependencies)
    DOMAIN_FORBIDDEN = {
        "fastapi",
        "sqlalchemy",
        "pydantic",
        "uvicorn",
        "httpx",
        "requests",
        "redis",
        "psycopg2",
        "asyncpg",
    }

    # Layer import rules: layer -> allowed imports
    LAYER_RULES = {
        "domain": set(),  # Domain imports NOTHING from other layers
        "application": {"domain"},  # Application may import domain only
        "api": {"application", "contracts"},  # API imports application + contracts
        "infrastructure": {
            "application",
            "domain",
        },  # Infrastructure imports app + domain
        "contracts": set(),  # Contracts are standalone
    }

    def __init__(self, backend_path: Path):
        self.backend_path = backend_path
        self.violations: List[Dict[str, str]] = []

    def check(self) -> bool:
        """Run all architecture checks. Returns True if all pass."""
        self.violations.clear()

        # Check domain layer for forbidden framework imports
        self._check_domain_purity()

        # Check layer boundary violations
        self._check_layer_boundaries()

        return len(self.violations) == 0

    def _check_domain_purity(self) -> None:
        """Ensure domain layer has no framework imports"""
        domain_path = self.backend_path / "domain"
        if not domain_path.exists():
            return

        for py_file in domain_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            imports = self._extract_imports(py_file)
            forbidden = imports & self.DOMAIN_FORBIDDEN

            if forbidden:
                self.violations.append(
                    {
                        "file": str(py_file.relative_to(self.backend_path.parent)),
                        "rule": "domain_purity",
                        "error": f"Domain layer imports forbidden frameworks: {', '.join(sorted(forbidden))}",
                    }
                )

    def _check_layer_boundaries(self) -> None:
        """Check that layers only import from allowed layers"""
        for layer, allowed_imports in self.LAYER_RULES.items():
            layer_path = self.backend_path / layer
            if not layer_path.exists():
                continue

            for py_file in layer_path.rglob("*.py"):
                if py_file.name == "__init__.py":
                    continue

                # Check for imports from other backend layers
                imports = self._extract_local_layer_imports(py_file)
                disallowed = imports - allowed_imports - {layer}

                if disallowed:
                    self.violations.append(
                        {
                            "file": str(py_file.relative_to(self.backend_path.parent)),
                            "rule": "layer_boundary",
                            "error": f"Layer '{layer}' imports from disallowed layers: {', '.join(sorted(disallowed))}",
                        }
                    )

    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Extract top-level package imports from a Python file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except SyntaxError:
            return set()

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Get root package name
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

        return imports

    def _extract_local_layer_imports(self, file_path: Path) -> Set[str]:
        """Extract imports from other backend layers"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except SyntaxError:
            return set()

        layer_imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("backend."):
                    # Extract layer name: backend.domain.* -> domain
                    parts = node.module.split(".")
                    if len(parts) >= 2:
                        layer_imports.add(parts[1])

        return layer_imports

    def print_violations(self) -> None:
        """Print violations in a CI-friendly format"""
        if not self.violations:
            print("✓ Architecture boundaries check passed")
            return

        print(f"✗ Architecture violations found ({len(self.violations)}):\n")
        for v in self.violations:
            print(f"  File: {v['file']}")
            print(f"  Rule: {v['rule']}")
            print(f"  Error: {v['error']}\n")


def main() -> int:
    """Entry point for architecture checker"""
    backend_path = Path(__file__).parent.parent / "backend"

    if not backend_path.exists():
        print("✗ Backend directory not found")
        return 1

    checker = ArchitectureChecker(backend_path)
    passed = checker.check()
    checker.print_violations()

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
