"""FastAPI dependency for database sessions."""

from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config.settings import settings


def _get_database_url() -> str:
    """Prefer TEST_DATABASE_URL in test environments."""
    return os.getenv("TEST_DATABASE_URL", settings.database_url)


_engine = create_engine(_get_database_url())
_SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session for a request."""
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()
