"""Unit tests for ModelPredictor."""
import pandas as pd
import pytest
from xgboost import XGBRegressor

from src.application.services.ml_service import TrainedModel
from src.infrastructure.ml.predictor import ModelPredictor


class TestModelPredictor:
    def setup_method(self):
        # Train a tiny model for testing
        X = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        y = pd.Series([0.5, 0.7, 0.9])
        model = XGBRegressor(n_estimators=5, max_depth=2)
        model.fit(X, y)
        self.trained = TrainedModel(
            model=model,
            metrics={},
            run_id="test-run",
            feature_names=["a", "b"],
        )
        self.predictor = ModelPredictor()

    def test_predict_returns_array(self):
        X = pd.DataFrame({"a": [1], "b": [4]})
        result = self.predictor.predict(self.trained, X)
        assert len(result) == 1

    def test_predict_raises_on_missing_columns(self):
        X = pd.DataFrame({"a": [1]})  # missing "b"
        with pytest.raises(ValueError, match="missing required columns"):
            self.predictor.predict(self.trained, X)
