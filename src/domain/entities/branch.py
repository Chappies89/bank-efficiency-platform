"""Branch entity.

Represents the permanent identity of a bank branch.
Time-varying performance data (FTE, opex, deposits) lives in
BranchObservation — one observation per branch per date.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Branch:
    """The permanent identity of a bank branch.

    Attributes:
        branch_id: Unique identifier for the branch.
        branch_name: Human-readable name.
        region: The province or region (e.g. "Gauteng", "Limpopo").
        opened_date: When the branch first opened.
        square_meters: Physical footprint, in square meters.
    """

    branch_id: int
    branch_name: str
    region: str
    opened_date: date
    square_meters: int
