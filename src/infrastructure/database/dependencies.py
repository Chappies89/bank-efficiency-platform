"""FastAPI dependency for database sessions."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config.settings import settings

_engine = create_engine(settings.database_url)
_SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session for a request."""
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()
