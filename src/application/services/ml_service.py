"""ML service — orchestrates XGBoost training and prediction.

This service sits in the application layer. It uses the infrastructure
layer (XGBoostTrainer, ModelPredictor) to do the actual work while
staying independent of specific ML frameworks. This keeps the domain
and application layers testable without spinning up ML dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from src.domain.value_objects.efficiency_score import EfficiencyScore


@dataclass
class TrainedModel:
    """The result of training — model object, metrics, and MLflow run ID.

    Attributes:
        model: The underlying trained estimator (e.g. XGBRegressor).
        metrics: Dict of metric names → values (e.g. {"rmse": 0.05}).
        run_id: MLflow run ID for auditability and model retrieval.
        feature_names: The feature columns the model expects.
    """

    model: Any
    metrics: dict[str, float] = field(default_factory=dict)
    run_id: str = ""
    feature_names: list[str] = field(default_factory=list)


class MLService:
    """Trains XGBoost models on DEA efficiency scores and predicts future efficiency."""

    def __init__(self, tracking_uri: str = "http://localhost:5000") -> None:
        self._tracking_uri = tracking_uri

    def train(
        self,
        features: pd.DataFrame,
        targets: pd.Series,
    ) -> TrainedModel:
        """Train an XGBoost model on features → efficiency scores.

        Args:
            features: N x M matrix of operational KPIs.
            targets: N-length series of DEA efficiency scores in [0, 1].

        Returns:
            A TrainedModel containing the estimator, metrics, and MLflow run_id.

        Raises:
            ValueError: If inputs are empty or their sizes mismatch.
        """
        # Deferred import so tests can run without ML dependencies installed
        from src.infrastructure.ml.trainer import XGBoostTrainer

        if features.empty:
            raise ValueError("Features cannot be empty")
        if targets.empty:
            raise ValueError("Targets cannot be empty")
        if len(features) != len(targets):
            raise ValueError(
                f"Feature and target lengths must match: "
                f"got {len(features)} features and {len(targets)} targets"
            )

        trainer = XGBoostTrainer(tracking_uri=self._tracking_uri)
        return trainer.train(features=features, targets=targets)

    def predict(
        self,
        model: TrainedModel,
        features: pd.DataFrame,
    ) -> list[EfficiencyScore]:
        """Predict efficiency scores for new observations.

        Args:
            model: A previously trained TrainedModel.
            features: N x M matrix of operational KPIs matching the training schema.

        Returns:
            A list of EfficiencyScore value objects.

        Raises:
            ValueError: If features are empty.
        """
        from src.infrastructure.ml.predictor import ModelPredictor

        if features.empty:
            raise ValueError("Features cannot be empty")

        predictor = ModelPredictor()
        raw_predictions = predictor.predict(model, features)

        return [
            EfficiencyScore(float(np.clip(p, 0.0, 1.0)))
            for p in raw_predictions
        ]
