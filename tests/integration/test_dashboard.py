"""Tests for dashboard data helpers."""
import os

import pytest
from sqlalchemy import create_engine

from src.infrastructure.database.models import Base


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Ensure tables exist in the test database."""
    db_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://bankuser:bankpass@localhost:5432/bank_efficiency",
    )
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    engine.dispose()


@pytest.mark.integration
class TestDashboardData:
    def test_load_branches_returns_dataframe(self) -> None:
        from src.presentation.dashboard.data import load_branches

        df = load_branches()
        assert hasattr(df, "columns")
        assert "branch_id" in df.columns or df.empty

    def test_load_latest_efficiency_returns_dataframe(self) -> None:
        from src.presentation.dashboard.data import load_latest_efficiency

        df = load_latest_efficiency()
        assert hasattr(df, "columns")

    def test_load_combined_has_expected_columns(self) -> None:
        from src.presentation.dashboard.data import (
            load_branches_with_efficiency,
        )

        df = load_branches_with_efficiency()
        expected = {"branch_id", "branch_name", "region"}
        assert expected.issubset(set(df.columns)) or df.empty
