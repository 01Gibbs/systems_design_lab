"""Contract Acceptor - Regenerates OpenAPI snapshot"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def accept_contracts() -> int:
    """Accept current OpenAPI schema as new snapshot"""
    backend_root = Path(__file__).parent.parent.parent.parent
    snapshot_path = backend_root / "openapi.json"

    try:
        from app.api.main import app

        schema = app.openapi()

        # Write snapshot
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, sort_keys=True)
            f.write("\n")

        print(f"✓ OpenAPI snapshot updated: {snapshot_path}")
        return 0

    except Exception as e:
        print(f"✗ Failed to generate OpenAPI schema: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(accept_contracts())
