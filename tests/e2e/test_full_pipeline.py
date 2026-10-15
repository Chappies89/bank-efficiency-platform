"""End-to-end test of the full DEA-ML pipeline.

This test exercises:
    1. Synthetic data generation
    2. Postgres persistence (branches + observations)
    3. DEA efficiency scoring
    4. ML model training (XGBoost)
    5. SHAP explainability
    6. The full pipeline works against a real database

It uses the test database (TEST_DATABASE_URL).
"""
from __future__ import annotations

import os
from datetime import date

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.application.services.dea_service import DEAService
from src.application.services.ml_service import MLService
from src.application.services.shap_service import ShapService
from src.infrastructure.database.models import Base
from src.infrastructure.database.repositories import (
    PostgresBranchRepository,
    PostgresDEARepository,
)
from src.infrastructure.external.synthetic_data_generator import (
    generate_branches,
    generate_observations,
)


@pytest.fixture(scope="module")
def engine():
    """Create a clean test database engine."""
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
def session(engine):
    session_factory = sessionmaker(bind=engine)
    s = session_factory()
    yield s
    s.rollback()
    s.close()


@pytest.mark.e2e
class TestFullPipeline:
    def test_end_to_end_dea_ml_shap(self, session) -> None:
        """Full pipeline: generate → persist → DEA → ML → SHAP."""

        # ---------------------------------------------------------
        # Step 1: Generate synthetic branches and observations
        # ---------------------------------------------------------
        branches = generate_branches(n=20, seed=42)
        assert len(branches) == 20

        observations = generate_observations(
            branches, start_date=date(2025, 1, 1), months=6, seed=42
        )
        assert len(observations) == 20 * 6  # 120 observations

        # ---------------------------------------------------------
        # Step 2: Persist to Postgres
        # ---------------------------------------------------------
        branch_repo = PostgresBranchRepository(session)
        for b in branches:
            branch_repo.save_branch(b)
        for o in observations:
            branch_repo.save_observation(o)
        session.commit()

        # Verify persistence
        count = session.execute(text("SELECT COUNT(*) FROM branches")).scalar_one()
        assert count == 20

        obs_count = session.execute(text("SELECT COUNT(*) FROM branch_observations")).scalar_one()
        assert obs_count == 120

        # ---------------------------------------------------------
        # Step 3: Run DEA on the latest month
        # ---------------------------------------------------------
        latest_date = date(2025, 6, 1)
        latest_obs = branch_repo.get_observations_for_date(latest_date)
        assert len(latest_obs) == 20

        dea = DEAService()
        scores = dea.calculate_efficiency(
            [o.to_input_vector() for o in latest_obs],
            [o.to_output_vector() for o in latest_obs],
        )
        assert len(scores) == 20
        assert all(0.0 <= s.value <= 1.0 for s in scores)
        assert any(s.value == 1.0 for s in scores)  # at least one on frontier

        # Persist DEA scores
        dea_repo = PostgresDEARepository(session)
        for obs, score in zip(latest_obs, scores, strict=False):
            dea_repo.save_score(obs.branch_id, score, latest_date)
        session.commit()

        dea_count = session.execute(text("SELECT COUNT(*) FROM dea_results")).scalar_one()
        assert dea_count == 20

        # ---------------------------------------------------------
        # Step 4: Train ML model on DEA scores
        # ---------------------------------------------------------
        # Build feature DataFrame from observations
        import pandas as pd

        features = pd.DataFrame(
            [
                {
                    "fte_count": o.fte_count,
                    "operational_expense": o.operational_expense,
                    "digital_transaction_ratio": o.digital_transaction_ratio,
                }
                for o in latest_obs
            ]
        )
        targets = pd.Series([s.value for s in scores])

        ml = MLService()
        model = ml.train(features, targets)
        assert model is not None
        assert "rmse" in model.metrics
        assert "r2" in model.metrics

        # ---------------------------------------------------------
        # Step 5: Predict efficiency on the same features
        # ---------------------------------------------------------
        predictions = ml.predict(model, features)
        assert len(predictions) == 20
        assert all(0.0 <= p.value <= 1.0 for p in predictions)

        # ---------------------------------------------------------
        # Step 6: SHAP explains a single prediction
        # ---------------------------------------------------------
        single_row = features.head(1)
        contributions = ShapService().explain(model, single_row, top_n=3)
        assert len(contributions) == 3
        assert all(hasattr(c, "feature") for c in contributions)
        assert all(hasattr(c, "contribution") for c in contributions)
        assert all(hasattr(c, "value") for c in contributions)
