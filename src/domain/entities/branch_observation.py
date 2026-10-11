"""BranchObservation entity.

A snapshot of a branch's performance at a specific point in time.
This is what feeds the DEA model — every observation for a given date
becomes one row in the DEA input/output matrix.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class BranchObservation:
    """A single snapshot of a branch's inputs and outputs at a date.

    Attributes:
        branch_id: Which branch this observation belongs to.
        observation_date: The date of the snapshot (e.g. 2026-06-30).
        fte_count: Full-time equivalent staff.
        operational_expense: Monthly operating cost in ZAR.
        deposit_volume: Total deposits in ZAR.
        loan_volume: Total loans issued in ZAR.
        new_accounts: Number of new accounts opened.
        digital_transaction_ratio: Fraction of digital transactions (0.0-1.0).
    """

    branch_id: int
    observation_date: date
    fte_count: int
    operational_expense: float
    deposit_volume: float
    loan_volume: float
    new_accounts: int
    digital_transaction_ratio: float

    def to_input_vector(self) -> list[float]:
        """The resources consumed by the branch at this point in time."""
        return [
            float(self.fte_count),
            float(self.operational_expense),
        ]

    def to_output_vector(self) -> list[float]:
        """The products produced by the branch at this point in time."""
        return [
            float(self.deposit_volume),
            float(self.loan_volume),
            float(self.new_accounts),
        ]
