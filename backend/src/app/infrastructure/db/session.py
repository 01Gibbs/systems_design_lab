"""Database Session Management"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Database URL will be injected from environment
engine: Any = None
async_session_maker: sessionmaker[Any] | None = None


def init_db(database_url: str) -> None:
    """Initialize database engine and session maker"""
    global engine, async_session_maker

    engine = create_async_engine(database_url, echo=False)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting DB session"""
    if async_session_maker is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with async_session_maker() as session:
        yield session
