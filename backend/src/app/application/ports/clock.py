"""Clock Port - Interface for time operations"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime


class Clock(ABC):
    """Port for clock operations - allows testing with fake time"""

    @abstractmethod
    def now(self) -> datetime:
        """Get current UTC datetime"""
        raise NotImplementedError
