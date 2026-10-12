"""XGBoost trainer with MLflow experiment tracking.

MLflow tracking is optional:
- If the tracking server is reachable, runs are logged remotely.
- If it isn't, training still completes and a warning is logged.
"""

from __future__ import annotations

import logging
from typing import Any

import mlflow
import mlflow.xgboost
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor

from src.application.services.ml_service import TrainedModel

logger = logging.getLogger(__name__)


class XGBoostTrainer:
    """Trains XGBoost regressors and logs them to MLflow (best-effort)."""

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
        """Train an XGBoost regressor and optionally log the run to MLflow."""
        params: dict[str, Any] = {
            "n_estimators": 100,
            "max_depth": 4,
            "learning_rate": 0.1,
            "objective": "reg:squarederror",
            "random_state": 42,
        }

        model = XGBRegressor(**params)
        model.fit(features, targets)

        predictions = model.predict(features)
        rmse = float(np.sqrt(mean_squared_error(targets, predictions)))
        r2 = float(r2_score(targets, predictions))

        run_id = self._log_to_mlflow_best_effort(model, params, rmse, r2)

        return TrainedModel(
            model=model,
            metrics={"rmse": rmse, "r2": r2},
            run_id=run_id,
            feature_names=list(features.columns),
        )

    def _log_to_mlflow_best_effort(
        self,
        model: XGBRegressor,
        params: dict[str, Any],
        rmse: float,
        r2: float,
    ) -> str:
        """Try to log to MLflow. If it fails, return an empty run_id.

        We set a short HTTP timeout (2s) and disable retries so tests
        fail fast when the MLflow server is offline (e.g., in CI).
        """
        import os

        os.environ["MLFLOW_HTTP_REQUEST_TIMEOUT"] = "2"
        os.environ["MLFLOW_HTTP_REQUEST_MAX_RETRIES"] = "0"

        try:
            mlflow.set_tracking_uri(self._tracking_uri)
            mlflow.set_experiment(self._experiment_name)
            with mlflow.start_run() as run:
                mlflow.log_params(params)
                mlflow.log_metric("rmse", rmse)
                mlflow.log_metric("r2", r2)
                mlflow.xgboost.log_model(model, artifact_path="model")
                return str(run.info.run_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "MLflow logging skipped (%s). Training still completed.", exc
            )
            return ""
