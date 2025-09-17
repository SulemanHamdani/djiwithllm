"""Database session and engine management."""
from __future__ import annotations

from typing import AsyncIterator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.models.base import Base

_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def configure_engine(database_url: Optional[str] = None) -> None:
    """Configure the SQLAlchemy engine using the provided database URL."""

    global _engine, _session_factory
    url = database_url or get_settings().database_url
    _engine = create_async_engine(url, future=True, echo=False)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


def get_engine() -> AsyncEngine:
    """Return the configured engine, initializing it if required."""

    global _engine
    if _engine is None:
        configure_engine()
    assert _engine is not None  # for mypy
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the session factory for creating sessions."""

    global _session_factory
    if _session_factory is None:
        configure_engine()
    assert _session_factory is not None
    return _session_factory


async def init_db() -> None:
    """Initialise database tables."""

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncIterator[AsyncSession]:
    """Yield a managed async database session."""

    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
