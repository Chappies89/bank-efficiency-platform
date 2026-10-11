"""Unit tests for BranchObservation entity."""
from datetime import date

import pytest

from src.domain.entities.branch_observation import BranchObservation


class TestBranchObservation:
    def setup_method(self) -> None:
        self.obs = BranchObservation(
            branch_id=1,
            observation_date=date(2026, 6, 30),
            fte_count=20,
            operational_expense=1_000_000.0,
            deposit_volume=50_000_000.0,
            loan_volume=30_000_000.0,
            new_accounts=500,
            digital_transaction_ratio=0.75,
        )

    def test_input_vector_length(self):
        assert len(self.obs.to_input_vector()) == 2

    def test_output_vector_length(self):
        assert len(self.obs.to_output_vector()) == 3

    def test_input_vector_values(self):
        assert self.obs.to_input_vector() == [20.0, 1_000_000.0]

    def test_output_vector_values(self):
        assert self.obs.to_output_vector() == [50_000_000.0, 30_000_000.0, 500.0]

    def test_observation_is_immutable(self):
        with pytest.raises(AttributeError):
            self.obs.fte_count = 999  # type: ignore[misc]

    def test_observation_has_date(self):
        assert self.obs.observation_date == date(2026, 6, 30)
