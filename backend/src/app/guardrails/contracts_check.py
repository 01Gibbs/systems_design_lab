"""Contract Checker - Prevents OpenAPI drift"""

from __future__ import annotations

import json
import sys
from pathlib import Path


class ContractChecker:
    """Validates OpenAPI contract against checked-in snapshot"""

    def __init__(self, backend_root: Path):
        self.backend_root = backend_root
        self.snapshot_path = backend_root / "openapi.json"
        self.violations: list[str] = []

    def check_drift(self) -> bool:
        """Check if current OpenAPI schema matches snapshot"""
        self.violations.clear()

        # Check if snapshot exists
        if not self.snapshot_path.exists():
            self.violations.append(
                "No OpenAPI snapshot found. Run 'make contracts-accept' to create initial snapshot."
            )
            return False

        # Load snapshot
        with open(self.snapshot_path, encoding="utf-8") as f:
            snapshot = json.load(f)

        # Generate current schema
        current_schema = self._generate_current_schema()

        if current_schema is None:
            self.violations.append(
                "Could not generate current OpenAPI schema. Ensure FastAPI app is importable."
            )
            return False

        # Compare
        if not self._schemas_equal(snapshot, current_schema):
            self.violations.append(
                "OpenAPI schema has changed. "
                "Review changes and run 'make contracts-accept' to update snapshot."
            )
            self._print_diff(snapshot, current_schema)
            return False

        return True

    def _generate_current_schema(self) -> dict[str, object] | None:
        """Generate OpenAPI schema from FastAPI app"""
        try:
            from app.api.main import app

            return app.openapi()
        except Exception as e:
            print(f"Error generating schema: {e}")
            return None

    def _schemas_equal(self, schema1: dict[str, object], schema2: dict[str, object]) -> bool:
        """Compare two schemas for equality"""
        json1 = json.dumps(schema1, sort_keys=True)
        json2 = json.dumps(schema2, sort_keys=True)
        return json1 == json2

    def _print_diff(self, old: dict[str, object], new: dict[str, object]) -> None:
        """Print high-level diff"""
        old_paths = self._extract_paths(old)
        new_paths = self._extract_paths(new)

        added = new_paths - old_paths
        removed = old_paths - new_paths

        if added:
            print(f"\n  Added endpoints: {', '.join(sorted(added))}")
        if removed:
            print(f"  Removed endpoints: {', '.join(sorted(removed))}")

        old_version = old.get("info", {}).get("version", "unknown")
        new_version = new.get("info", {}).get("version", "unknown")
        if old_version != new_version:
            print(f"  Version: {old_version} → {new_version}")

    def _extract_paths(self, schema: dict[str, object]) -> set[str]:
        """Extract all paths from schema"""
        paths = schema.get("paths", {})
        return {f"{method.upper()} {path}" for path, methods in paths.items() for method in methods}

    def print_violations(self) -> None:
        """Print violations"""
        if not self.violations:
            print("✓ Contract drift check passed")
            return

        print("✗ Contract violations found:\n")
        for v in self.violations:
            print(f"  {v}\n")


def main() -> int:
    """Entry point"""
    backend_root = Path(__file__).parent.parent.parent.parent

    checker = ContractChecker(backend_root)
    passed = checker.check_drift()
    checker.print_violations()

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
