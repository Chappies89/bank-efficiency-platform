"""XGBoost trainer with MLflow experiment tracking."""

from __future__ import annotations

from typing import Any

import mlflow
import mlflow.xgboost
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor

from src.application.services.ml_service import TrainedModel


class XGBoostTrainer:
    """Trains XGBoost regressors and logs them to MLflow."""

    def __init__(
        self,
        tracking_uri: str = "http://localhost:5000",
        experiment_name: str = "dea-efficiency",
    ) -> None:
        self._tracking_uri = tracking_uri
        self._experiment_name = experiment_name

    def train(
        self,
        features: pd.DataFrame,
        targets: pd.Series,
    ) -> TrainedModel:
        """Train an XGBoost regressor and log the run to MLflow."""
        mlflow.set_tracking_uri(self._tracking_uri)
        mlflow.set_experiment(self._experiment_name)

        params: dict[str, Any] = {
            "n_estimators": 100,
            "max_depth": 4,
            "learning_rate": 0.1,
            "objective": "reg:squarederror",
            "random_state": 42,
        }

        with mlflow.start_run() as run:
            mlflow.log_params(params)

            model = XGBRegressor(**params)
            model.fit(features, targets)

            predictions = model.predict(features)
            rmse = float(np.sqrt(mean_squared_error(targets, predictions)))
            r2 = float(r2_score(targets, predictions))

            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("r2", r2)
            mlflow.xgboost.log_model(model, artifact_path="model")

            return TrainedModel(
                model=model,
                metrics={"rmse": rmse, "r2": r2},
                run_id=run.info.run_id,
                feature_names=list(features.columns),
            )
