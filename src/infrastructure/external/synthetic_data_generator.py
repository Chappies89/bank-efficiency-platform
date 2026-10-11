"""Generate synthetic bank branch data for demos and tests."""

from __future__ import annotations

from datetime import date

import numpy as np

from src.domain.entities.branch import Branch
from src.domain.entities.branch_observation import BranchObservation

REGIONS = ["Gauteng", "Western Cape", "KwaZulu-Natal", "Limpopo", "Mpumalanga"]


def generate_branches(n: int = 500, seed: int = 42) -> list[Branch]:
    """Generate n synthetic branches with realistic attributes."""
    rng = np.random.default_rng(seed)
    branches: list[Branch] = []
    for i in range(1, n + 1):
        region = str(REGIONS[rng.integers(0, len(REGIONS))])
        branches.append(
            Branch(
                branch_id=i,
                branch_name=f"Branch-{i:04d}",
                region=region,
                opened_date=date(
                    int(rng.integers(1995, 2020)),
                    int(rng.integers(1, 13)),
                    int(rng.integers(1, 29)),
                ),
                square_meters=int(rng.integers(200, 2000)),
            )
        )
    return branches


def generate_observations(
    branches: list[Branch],
    start_date: date,
    months: int = 36,
    seed: int = 42,
) -> list[BranchObservation]:
    """Generate monthly observations for each branch over N months."""
    from dateutil.relativedelta import relativedelta

    rng = np.random.default_rng(seed)
    observations: list[BranchObservation] = []

    for branch in branches:
        base_fte = rng.normal(20, 6)
        base_opex = base_fte * 50000 + rng.normal(0, 100000)
        base_deposits = base_fte * 2_000_000 + rng.normal(0, 5_000_000)
        base_loans = base_fte * 1_500_000 + rng.normal(0, 4_000_000)

        for m in range(months):
            seasonal = 1.0 + 0.05 * np.sin(2 * np.pi * m / 12)
            noise = rng.normal(1.0, 0.03)
            observations.append(
                BranchObservation(
                    branch_id=branch.branch_id,
                    observation_date=start_date + relativedelta(months=m),
                    fte_count=max(1, int(base_fte * seasonal * noise)),
                    operational_expense=abs(float(base_opex * seasonal * noise)),
                    deposit_volume=abs(float(base_deposits * seasonal * noise)),
                    loan_volume=abs(float(base_loans * seasonal * noise)),
                    new_accounts=max(0, int(rng.normal(50, 15))),
                    digital_transaction_ratio=float(np.clip(rng.normal(0.65, 0.15), 0.0, 1.0)),
                )
            )
    return observations
