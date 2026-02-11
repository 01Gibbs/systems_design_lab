"""System Clock Implementation"""

from __future__ import annotations

from datetime import datetime, timezone

from app.application.ports.clock import Clock


class SystemClock(Clock):
    """
    System clock implementation using real system time.

    Can be swapped with FakeClock for testing.
    """

    def now(self) -> datetime:
        return datetime.now(timezone.utc)
