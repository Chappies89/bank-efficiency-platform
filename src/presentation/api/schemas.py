"""Pydantic request/response schemas for the API."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class BranchResponse(BaseModel):
    """A bank branch."""

    branch_id: int
    branch_name: str
    region: str
    opened_date: date
    square_meters: int


class EfficiencyResponse(BaseModel):
    """An efficiency score for a branch."""

    branch_id: int
    observation_date: date
    efficiency_score: float = Field(ge=0.0, le=1.0)
    is_efficient: bool


class PredictionRequest(BaseModel):
    """Input features for a prediction."""

    fte_count: int = Field(gt=0)
    operational_expense: float = Field(gt=0)
    digital_transaction_ratio: float = Field(ge=0.0, le=1.0)


class PredictionResponse(BaseModel):
    """A predicted efficiency score."""

    model_config = {"protected_namespaces": ()}

    predicted_efficiency: float = Field(ge=0.0, le=1.0)
    model_run_id: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
