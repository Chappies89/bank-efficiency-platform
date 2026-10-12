"""Integration tests for the FastAPI layer."""
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from src.infrastructure.database.models import Base
from src.presentation.api.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    # Ensure tables exist before any test runs
    db_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://bankuser:bankpass@localhost:5432/bank_efficiency",
    )
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    engine.dispose()
    return TestClient(app)


@pytest.mark.integration
class TestHealthEndpoint:
    def test_health_returns_ok(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"


@pytest.mark.integration
class TestBranchesEndpoint:
    def test_list_branches_returns_list(self, client: TestClient) -> None:
        response = client.get("/api/branches")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.integration
class TestPredictEndpoint:
    def test_predict_returns_valid_efficiency(self, client: TestClient) -> None:
        payload = {
            "fte_count": 20,
            "operational_expense": 1_000_000.0,
            "digital_transaction_ratio": 0.75,
        }
        response = client.post("/api/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert 0.0 <= data["predicted_efficiency"] <= 1.0
        assert "model_run_id" in data

    def test_predict_rejects_invalid_input(self, client: TestClient) -> None:
        payload = {
            "fte_count": 0,  # must be > 0
            "operational_expense": 1_000_000.0,
            "digital_transaction_ratio": 0.75,
        }
        response = client.post("/api/predict", json=payload)
        assert response.status_code == 422


@pytest.mark.integration
class TestOpenAPI:
    def test_openapi_spec_available(self, client: TestClient) -> None:
        response = client.get("/openapi.json")
        assert response.status_code == 200
        spec = response.json()
        assert spec["info"]["title"] == "Bank Efficiency Platform API"
        assert "/health" in spec["paths"]
