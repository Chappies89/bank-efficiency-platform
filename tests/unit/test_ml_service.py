"""Unit tests for the MLService.

These tests define the contract for the ML layer:
- Trains XGBoost on features + targets
- Returns a TrainedModel with metrics and MLflow run_id
- Predicts efficiency scores as EfficiencyScore value objects
- Enforces input validation
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.application.services.ml_service import MLService, TrainedModel
from src.domain.value_objects.efficiency_score import EfficiencyScore


@pytest.fixture
def sample_features() -> pd.DataFrame:
    """50 synthetic feature rows."""
    rng = np.random.default_rng(42)
    return pd.DataFrame(
        {
            "fte_count": rng.integers(5, 50, size=50),
            "operational_expense": rng.uniform(100_000, 2_000_000, size=50),
            "digital_transaction_ratio": rng.uniform(0.3, 0.95, size=50),
        }
    )


@pytest.fixture
def sample_targets() -> pd.Series:
    """50 synthetic efficiency scores in [0, 1]."""
    rng = np.random.default_rng(43)
    return pd.Series(rng.uniform(0.4, 1.0, size=50))


class TestMLServiceTraining:
    def test_train_returns_trained_model(
        self, sample_features: pd.DataFrame, sample_targets: pd.Series
    ) -> None:
        service = MLService()
        model = service.train(sample_features, sample_targets)
        assert isinstance(model, TrainedModel)

    def test_trained_model_has_run_id(
        self, sample_features: pd.DataFrame, sample_targets: pd.Series
    ) -> None:
        service = MLService()
        model = service.train(sample_features, sample_targets)
        assert model.run_id is not None
        assert isinstance(model.run_id, str)
        assert len(model.run_id) > 0

    def test_trained_model_has_metrics(
        self, sample_features: pd.DataFrame, sample_targets: pd.Series
    ) -> None:
        service = MLService()
        model = service.train(sample_features, sample_targets)
        assert "rmse" in model.metrics
        assert "r2" in model.metrics
        assert isinstance(model.metrics["rmse"], float)
        assert isinstance(model.metrics["r2"], float)

    def test_train_raises_on_empty_features(
        self, sample_targets: pd.Series
    ) -> None:
        service = MLService()
        with pytest.raises(ValueError, match="cannot be empty"):
            service.train(pd.DataFrame(), sample_targets)

    def test_train_raises_on_empty_targets(
        self, sample_features: pd.DataFrame
    ) -> None:
        service = MLService()
        with pytest.raises(ValueError, match="cannot be empty"):
            service.train(sample_features, pd.Series(dtype=float))

    def test_train_raises_on_shape_mismatch(
        self, sample_features: pd.DataFrame
    ) -> None:
        service = MLService()
        mismatched = pd.Series(np.random.uniform(0.5, 1.0, size=30))
        with pytest.raises(ValueError, match="must match"):
            service.train(sample_features, mismatched)


class TestMLServicePrediction:
    def test_predict_returns_efficiency_scores(
        self, sample_features: pd.DataFrame, sample_targets: pd.Series
    ) -> None:
        service = MLService()
        model = service.train(sample_features, sample_targets)
        predictions = service.predict(model, sample_features)
        assert len(predictions) == len(sample_features)
        assert all(isinstance(p, EfficiencyScore) for p in predictions)

    def test_predict_clamps_to_valid_range(
        self, sample_features: pd.DataFrame, sample_targets: pd.Series
    ) -> None:
        service = MLService()
        model = service.train(sample_features, sample_targets)
        predictions = service.predict(model, sample_features)
        for p in predictions:
            assert 0.0 <= p.value <= 1.0

    def test_predict_raises_on_empty_features(
        self, sample_features: pd.DataFrame, sample_targets: pd.Series
    ) -> None:
        service = MLService()
        model = service.train(sample_features, sample_targets)
        with pytest.raises(ValueError, match="cannot be empty"):
            service.predict(model, pd.DataFrame())
