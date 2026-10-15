"""Integration tests against a real PostgreSQL database."""
from __future__ import annotations

import os
from collections.abc import Generator
from datetime import date

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from src.domain.entities.branch import Branch
from src.domain.entities.branch_observation import BranchObservation
from src.domain.value_objects.efficiency_score import EfficiencyScore
from src.infrastructure.database.models import Base
from src.infrastructure.database.repositories import (
    PostgresBranchRepository,
    PostgresDEARepository,
)


@pytest.fixture(scope="module")
def engine() -> Generator[Engine, None, None]:
    """Create a test database engine."""
    db_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://bankuser:bankpass@localhost:5432/bank_efficiency",
    )
    eng = create_engine(db_url)
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def session(engine: Engine) -> Generator[Session, None, None]:
    """Provide a transactional database session."""
    session_factory = sessionmaker(bind=engine)
    s = session_factory()
    yield s
    s.rollback()
    s.close()


@pytest.mark.integration
class TestPostgresBranchRepository:
    def test_save_and_retrieve_branch(self, session: Session) -> None:
        repo = PostgresBranchRepository(session)
        repo.save_branch(Branch(1001, "Sandton", "Gauteng", date(2010, 3, 1), 1200))
        session.commit()
        row = session.execute(
            text("SELECT branch_name FROM branches WHERE branch_id = 1001")
        ).scalar_one()
        assert row == "Sandton"

    def test_save_and_retrieve_observation(self, session: Session) -> None:
        repo = PostgresBranchRepository(session)
        repo.save_branch(Branch(1002, "Rosebank", "Gauteng", date(2015, 6, 1), 800))
        session.commit()
        repo.save_observation(
            BranchObservation(
                branch_id=1002,
                observation_date=date(2026, 6, 30),
                fte_count=20,
                operational_expense=1_000_000.0,
                deposit_volume=50_000_000.0,
                loan_volume=30_000_000.0,
                new_accounts=500,
                digital_transaction_ratio=0.75,
            )
        )
        session.commit()
        observations = repo.get_observations_for_date(date(2026, 6, 30))
        assert any(o.branch_id == 1002 for o in observations)


@pytest.mark.integration
class TestPostgresDEARepository:
    def test_save_and_retrieve_score(self, session: Session) -> None:
        branch_repo = PostgresBranchRepository(session)
        branch_repo.save_branch(Branch(1003, "Menlyn", "Gauteng", date(2018, 6, 1), 900))
        session.commit()
        repo = PostgresDEARepository(session)
        repo.save_score(1003, EfficiencyScore(0.87), date(2026, 6, 30))
        session.commit()
        score = repo.get_score(1003)
        assert score is not None
        assert score.value == pytest.approx(0.87)
