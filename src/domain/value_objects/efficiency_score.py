"""EfficiencyScore value object.

Represents a DEA efficiency score. Must be between 0.0 (fully inefficient)
and 1.0 (fully efficient). Immutable by design.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EfficiencyScore:
    """Immutable value object representing a DEA efficiency score.

    Attributes:
        value: A float between 0.0 and 1.0 inclusive.

    Raises:
        ValueError: If value is not between 0.0 and 1.0.
    """

    value: float

    def __post_init__(self) -> None:
        if not isinstance(self.value, int | float):
            raise ValueError(f"Efficiency score must be numeric, got {type(self.value)}")
        if not (0.0 <= self.value <= 1.0):
            raise ValueError(f"Efficiency score must be between 0.0 and 1.0, got {self.value}")

    def is_efficient(self) -> bool:
        """Return True if the score is 1.0 (on the efficiency frontier)."""
        return self.value == 1.0

    def is_inefficient(self) -> bool:
        """Return True if the score is below 1.0."""
        return self.value < 1.0
