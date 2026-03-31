"""Database connection factories and configuration.

Provides:
- SQLAlchemy engine setup with connection pooling
- Session factory helpers
- Context manager for transactional work
- Health check utility
- Graceful connection disposal
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from ...app.config import SETTINGS


# Lazy-initialized engine singleton
_engine: Optional[Engine] = None
_SessionFactory: Optional[sessionmaker] = None


def _create_engine() -> Engine:
    """Create a new SQLAlchemy engine using configuration values.

    Pooling defaults are conservative and suitable for API workloads.
    """
    # Pool configuration (tunable via env using SQLAlchemy URL query too)
    pool_size = 5
    max_overflow = 10
    pool_timeout = 30  # seconds
    pool_recycle = 1800  # seconds (30m) to avoid stale connections

    engine = create_engine(
        SETTINGS.database.primary_url,
        pool_pre_ping=True,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
        future=True,
    )
    return engine


def get_engine(reset: bool = False) -> Engine:
    """Return a process-wide Engine instance; recreate if reset is True."""
    global _engine
    if reset or _engine is None:
        _engine = _create_engine()
    return _engine


def get_session_factory() -> sessionmaker:
    """Return a configured sessionmaker bound to the engine."""
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, expire_on_commit=False)
    return _SessionFactory


def get_session() -> Session:
    """Create a new Session bound to the shared engine."""
    return get_session_factory()()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations.

    Commits on success, rolls back on error, and always closes session.
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def health_check() -> bool:
    """Return True if the database is reachable and responsive."""
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


def dispose_engine() -> None:
    """Dispose the engine and all underlying connection pools (graceful close)."""
    global _engine, _SessionFactory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionFactory = None
