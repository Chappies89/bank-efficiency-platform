"""Unit tests for the SHAP explainability service."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from xgboost import XGBRegressor

from src.application.services.ml_service import TrainedModel
from src.application.services.shap_service import (
    FeatureContribution,
    ShapService,
)


@pytest.fixture
def trained_model() -> TrainedModel:
    """A tiny XGBoost model trained on synthetic features."""
    rng = np.random.default_rng(42)
    features = pd.DataFrame(
        {
            "fte_count": rng.integers(5, 50, size=100),
            "operational_expense": rng.uniform(100_000, 2_000_000, size=100),
            "digital_transaction_ratio": rng.uniform(0.3, 0.95, size=100),
        }
    )
    targets = pd.Series(rng.uniform(0.4, 1.0, size=100))

    model = XGBRegressor(n_estimators=10, max_depth=3)
    model.fit(features, targets)

    return TrainedModel(
        model=model,
        metrics={"rmse": 0.0, "r2": 0.0},
        run_id="test-run",
        feature_names=["fte_count", "operational_expense", "digital_transaction_ratio"],
    )


@pytest.fixture
def single_row_features() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "fte_count": [20],
            "operational_expense": [1_000_000.0],
            "digital_transaction_ratio": [0.75],
        }
    )


class TestShapService:
    def test_explain_returns_contributions(
        self, trained_model: TrainedModel, single_row_features: pd.DataFrame
    ) -> None:
        service = ShapService()
        result = service.explain(trained_model, single_row_features)
        assert len(result) > 0
        assert all(isinstance(c, FeatureContribution) for c in result)

    def test_explain_returns_top_n(
        self, trained_model: TrainedModel, single_row_features: pd.DataFrame
    ) -> None:
        service = ShapService()
        result = service.explain(trained_model, single_row_features, top_n=2)
        assert len(result) == 2

    def test_explain_sorts_by_absolute_contribution(
        self, trained_model: TrainedModel, single_row_features: pd.DataFrame
    ) -> None:
        service = ShapService()
        result = service.explain(trained_model, single_row_features, top_n=3)
        magnitudes = [abs(c.contribution) for c in result]
        assert magnitudes == sorted(magnitudes, reverse=True)

    def test_explain_returns_feature_names(
        self, trained_model: TrainedModel, single_row_features: pd.DataFrame
    ) -> None:
        service = ShapService()
        result = service.explain(trained_model, single_row_features)
        feature_names = {c.feature for c in result}
        assert feature_names.issubset(
            {"fte_count", "operational_expense", "digital_transaction_ratio"}
        )

    def test_explain_raises_on_empty_features(self, trained_model: TrainedModel) -> None:
        service = ShapService()
        with pytest.raises(ValueError, match="cannot be empty"):
            service.explain(trained_model, pd.DataFrame())

    def test_explain_raises_on_multiple_rows(self, trained_model: TrainedModel) -> None:
        service = ShapService()
        features = pd.DataFrame(
            {
                "fte_count": [10, 20],
                "operational_expense": [500_000.0, 1_000_000.0],
                "digital_transaction_ratio": [0.5, 0.8],
            }
        )
        with pytest.raises(ValueError, match="single prediction"):
            service.explain(trained_model, features)
