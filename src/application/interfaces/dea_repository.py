"""Abstract repository interface for persisting DEA results."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from src.domain.value_objects.efficiency_score import EfficiencyScore


class DEARepository(ABC):
    """Interface for persisting and retrieving DEA efficiency scores."""

    @abstractmethod
    def save_score(
        self,
        branch_id: int,
        score: EfficiencyScore,
        observation_date: date,
    ) -> None:
        """Save an efficiency score for a given branch and observation date."""

    @abstractmethod
    def get_score(self, branch_id: int) -> EfficiencyScore | None:
        """Retrieve the most recent efficiency score for a branch."""
