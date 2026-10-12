"""Prediction endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from src.presentation.api.schemas import (
    PredictionRequest,
    PredictionResponse,
)

router = APIRouter(prefix="/api", tags=["predictions"])


@router.post("/predict", response_model=PredictionResponse)
def predict_efficiency(request: PredictionRequest) -> PredictionResponse:
    """Predict efficiency for new branch KPIs.

    Note: In production this would load a persisted model from MLflow.
    For now we return a deterministic stub based on the input, since
    training a model on every request is inefficient.
    """
    # Simple deterministic placeholder prediction
    # (Real implementation would load a persisted model by run_id)

    # Placeholder: weighted score in [0, 1]
    score = (
        0.4 * min(request.digital_transaction_ratio, 1.0)
        + 0.3 * min(1.0, request.fte_count / 50)
        + 0.3 * min(1.0, 1_000_000 / max(request.operational_expense, 1))
    )
    score = max(0.0, min(1.0, score))

    return PredictionResponse(
        predicted_efficiency=score,
        model_run_id="stub-model-v0",
    )
