"""Contract Drift Checker - Prevents silent OpenAPI schema changes"""
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional


class ContractChecker:
    """Validates OpenAPI contract against checked-in snapshot"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.snapshot_path = repo_root / "openapi.json"
        self.violations: list[str] = []

    def check_drift(self, current_schema: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if current OpenAPI schema matches snapshot.
        Returns True if no drift detected.
        """
        self.violations.clear()

        # If no snapshot exists, this is the first run
        if not self.snapshot_path.exists():
            self.violations.append(
                "No OpenAPI snapshot found. Run 'make contracts-accept' to create initial snapshot."
            )
            return False

        # Load snapshot
        with open(self.snapshot_path, "r", encoding="utf-8") as f:
            snapshot = json.load(f)

        # If current_schema not provided, try to generate it
        if current_schema is None:
            current_schema = self._generate_current_schema()

        if current_schema is None:
            self.violations.append(
                "Could not generate current OpenAPI schema. Ensure FastAPI app is importable."
            )
            return False

        # Compare schemas
        if not self._schemas_equal(snapshot, current_schema):
            self.violations.append(
                "OpenAPI schema has changed. Review changes and run 'make contracts-accept' to update snapshot."
            )
            self._print_diff(snapshot, current_schema)
            return False

        return True

    def accept_changes(self, schema: Optional[Dict[str, Any]] = None) -> bool:
        """
        Accept current schema as new snapshot.
        Returns True if successful.
        """
        if schema is None:
            schema = self._generate_current_schema()

        if schema is None:
            print("✗ Could not generate OpenAPI schema")
            return False

        # Write snapshot
        with open(self.snapshot_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, sort_keys=True)
            f.write("\n")  # Add trailing newline

        print(f"✓ OpenAPI snapshot updated: {self.snapshot_path}")
        return True

    def _generate_current_schema(self) -> Optional[Dict[str, Any]]:
        """Generate OpenAPI schema from FastAPI app"""
        try:
            # Try to import main FastAPI app
            # This will be implemented once FastAPI app exists
            # For now, return None to indicate app not ready
            return None
        except ImportError:
            return None

    def _schemas_equal(self, schema1: Dict[str, Any], schema2: Dict[str, Any]) -> bool:
        """Compare two schemas for equality (normalized)"""
        # Normalize and compare
        json1 = json.dumps(schema1, sort_keys=True)
        json2 = json.dumps(schema2, sort_keys=True)
        return json1 == json2

    def _print_diff(self, old: Dict[str, Any], new: Dict[str, Any]) -> None:
        """Print high-level diff between schemas"""
        old_paths = self._extract_paths(old)
        new_paths = self._extract_paths(new)

        added = new_paths - old_paths
        removed = old_paths - new_paths

        if added:
            print(f"\n  Added endpoints: {', '.join(sorted(added))}")
        if removed:
            print(f"  Removed endpoints: {', '.join(sorted(removed))}")

        # Check version changes
        old_version = old.get("info", {}).get("version", "unknown")
        new_version = new.get("info", {}).get("version", "unknown")
        if old_version != new_version:
            print(f"  Version: {old_version} → {new_version}")

    def _extract_paths(self, schema: Dict[str, Any]) -> set[str]:
        """Extract all paths from OpenAPI schema"""
        paths = schema.get("paths", {})
        return {f"{method.upper()} {path}" for path, methods in paths.items() for method in methods}

    def print_violations(self) -> None:
        """Print violations in CI-friendly format"""
        if not self.violations:
            print("✓ Contract drift check passed")
            return

        print(f"✗ Contract violations found:\n")
        for v in self.violations:
            print(f"  {v}\n")


def main() -> int:
    """Entry point for contract checker"""
    repo_root = Path(__file__).parent.parent

    checker = ContractChecker(repo_root)
    passed = checker.check_drift()
    checker.print_violations()

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
