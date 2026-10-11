"""Abstract repository interface for persisting DEA results.

The application layer depends on this interface, not on any specific
database. This is the Dependency Inversion Principle — depend on
abstractions, not on concretions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.value_objects.efficiency_score import EfficiencyScore


class DEARepository(ABC):
    """Interface for persisting and retrieving DEA efficiency scores."""

    @abstractmethod
    def save_score(self, branch_id: int, score: EfficiencyScore) -> None:
        """Save an efficiency score for a given branch."""

    @abstractmethod
    def get_score(self, branch_id: int) -> EfficiencyScore | None:
        """Retrieve the most recent efficiency score for a branch."""
