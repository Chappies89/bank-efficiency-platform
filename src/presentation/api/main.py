"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI

from src.presentation.api.routes.branches import router as branches_router
from src.presentation.api.routes.predictions import router as predictions_router
from src.presentation.api.schemas import HealthResponse

app = FastAPI(
    title="Bank Efficiency Platform API",
    description=("DEA-ML hybrid platform for measuring and predicting bank " "branch efficiency."),
    version="0.1.0",
)

app.include_router(branches_router)
app.include_router(predictions_router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok", version=app.version)
