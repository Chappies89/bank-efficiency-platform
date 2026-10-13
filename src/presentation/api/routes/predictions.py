"""Prediction endpoint with SHAP explanations."""

from __future__ import annotations

import numpy as np
import pandas as pd
from fastapi import APIRouter
from xgboost import XGBRegressor

from src.application.services.ml_service import TrainedModel
from src.application.services.shap_service import ShapService
from src.presentation.api.schemas import (
    FeatureContribution,
    PredictionRequest,
    PredictionResponse,
)

router = APIRouter(prefix="/api", tags=["predictions"])


def _get_placeholder_model() -> TrainedModel:
    """Build a tiny inline XGBoost model for demo predictions."""
    rng = np.random.default_rng(42)
    features = pd.DataFrame(
        {
            "fte_count": rng.integers(5, 50, size=200),
            "operational_expense": rng.uniform(100_000, 2_000_000, size=200),
            "digital_transaction_ratio": rng.uniform(0.3, 0.95, size=200),
        }
    )
    targets = pd.Series(
        0.4 * features["digital_transaction_ratio"]
        + 0.3 * (features["fte_count"] / 50).clip(0, 1)
        + 0.3 * (1_000_000 / features["operational_expense"]).clip(0, 1)
    )

    model = XGBRegressor(n_estimators=50, max_depth=4, random_state=42)
    model.fit(features, targets)

    return TrainedModel(
        model=model,
        metrics={},
        run_id="demo-model-v1",
        feature_names=list(features.columns),
    )


@router.post("/predict", response_model=PredictionResponse)
def predict_efficiency(request: PredictionRequest) -> PredictionResponse:
    """Predict efficiency for new branch KPIs, with SHAP explanation."""
    features = pd.DataFrame(
        {
            "fte_count": [request.fte_count],
            "operational_expense": [request.operational_expense],
            "digital_transaction_ratio": [request.digital_transaction_ratio],
        }
    )

    model = _get_placeholder_model()

    raw = float(model.model.predict(features)[0])
    score = max(0.0, min(1.0, raw))

    contributions = ShapService().explain(model, features, top_n=3)

    return PredictionResponse(
        predicted_efficiency=score,
        model_run_id=model.run_id,
        top_drivers=[
            FeatureContribution(
                feature=c.feature,
                contribution=c.contribution,
                value=c.value,
            )
            for c in contributions
        ],
    )
