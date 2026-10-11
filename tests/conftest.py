"""Shared pytest fixtures for all test stages."""
import os

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

import pytest


def pytest_collection_modifyitems(config, items):
    """Automatically apply markers based on test folder location.

    This maps folders to markers so that CI commands like
    `pytest tests/unit/ -m unit` work without requiring manual markers.
    """
    import pathlib

    folder_to_marker = {
        "unit": "unit",
        "integration": "integration",
        "e2e": "e2e",
        "performance": "performance",
        "business": "business",
        "smoke": "smoke",
    }

    for item in items:
        item_path = pathlib.Path(str(item.fspath))
        for folder, marker_name in folder_to_marker.items():
            if folder in item_path.parts:
                item.add_marker(getattr(pytest.mark, marker_name))
                break


@pytest.fixture(scope="session")
def test_database_url():
    """Test database URL."""
    return os.getenv(
        "TEST_DATABASE_URL", "postgresql://bankuser:bankpass@localhost:5432/bank_efficiency_test"
    )


@pytest.fixture(scope="session")
def db_engine(test_database_url):
    """Create a test database engine."""
    engine = create_engine(test_database_url)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Provide a transactional database session for each test."""
    session_factory = sessionmaker(bind=db_engine)
    session = session_factory()
    try:
        yield session
        session.rollback()
    finally:
        session.close()


@pytest.fixture
def client():
    """FastAPI test client."""
    from src.presentation.api.main import app

    return TestClient(app)


@pytest.fixture
def synthetic_dataframe():
    """Sample synthetic branch data for tests."""
    return pd.DataFrame(
        {
            "branch_id": [1, 2, 3, 4, 5],
            "fte_count": [15, 25, 20, 10, 30],
            "operational_expense": [750000, 1250000, 1000000, 500000, 1500000],
            "deposit_volume": [50000000, 100000000, 75000000, 25000000, 125000000],
            "digital_ratio": [0.75, 0.85, 0.80, 0.60, 0.90],
            "age_years": [5, 10, 8, 15, 3],
        }
    )


@pytest.fixture
def seeded_db(db_session):
    """Database with test branches loaded."""
    from src.infrastructure.external.synthetic_data_generator import generate

    generate(n_branches=10, session=db_session)
    return db_session
