"""Unit tests for the synthetic data generator."""
from __future__ import annotations

from datetime import date

from src.infrastructure.external.synthetic_data_generator import (
    generate_branches,
    generate_observations,
)


class TestGenerateBranches:
    def test_returns_requested_number_of_branches(self) -> None:
        branches = generate_branches(n=10, seed=42)
        assert len(branches) == 10

    def test_branches_have_unique_ids(self) -> None:
        branches = generate_branches(n=50, seed=42)
        ids = [b.branch_id for b in branches]
        assert len(ids) == len(set(ids))

    def test_branches_have_valid_region(self) -> None:
        branches = generate_branches(n=20, seed=42)
        valid = {"Gauteng", "Western Cape", "KwaZulu-Natal", "Limpopo", "Mpumalanga"}
        for b in branches:
            assert b.region in valid

    def test_generator_is_deterministic_with_seed(self) -> None:
        b1 = generate_branches(n=5, seed=1)
        b2 = generate_branches(n=5, seed=1)
        assert b1 == b2

    def test_different_seeds_produce_different_data(self) -> None:
        b1 = generate_branches(n=5, seed=1)
        b2 = generate_branches(n=5, seed=2)
        assert b1 != b2


class TestGenerateObservations:
    def test_returns_branch_count_times_months(self) -> None:
        branches = generate_branches(n=3, seed=42)
        observations = generate_observations(branches, date(2024, 1, 1), months=12, seed=42)
        assert len(observations) == 3 * 12

    def test_digital_transaction_ratio_is_between_0_and_1(self) -> None:
        branches = generate_branches(n=5, seed=42)
        observations = generate_observations(branches, date(2024, 1, 1), months=6, seed=42)
        for o in observations:
            assert 0.0 <= o.digital_transaction_ratio <= 1.0

    def test_fte_count_is_positive(self) -> None:
        branches = generate_branches(n=5, seed=42)
        observations = generate_observations(branches, date(2024, 1, 1), months=6, seed=42)
        for o in observations:
            assert o.fte_count >= 1

    def test_observation_dates_are_monthly(self) -> None:
        branches = generate_branches(n=1, seed=42)
        observations = generate_observations(branches, date(2024, 1, 1), months=3, seed=42)
        dates = [o.observation_date for o in observations]
        assert dates[0] == date(2024, 1, 1)
        assert dates[1] == date(2024, 2, 1)
        assert dates[2] == date(2024, 3, 1)
