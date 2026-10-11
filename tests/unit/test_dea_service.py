"""Unit tests for DEA service.

SKIPPED — will be implemented during Stage 2 (Integration).
"""
import pytest

pytestmark = pytest.mark.skip(reason="DEAService not implemented yet — Stage 2 pending")


class TestDEAService:
    def test_dea_returns_scores_for_each_branch(self):
        inputs = [[10, 1000], [20, 2000], [15, 1500]]
        outputs = [[100], [200], [150]]
        from src.application.services.dea_service import DEAService
        service = DEAService()
        scores = service.calculate_efficiency(inputs, outputs)
        assert len(scores) == 3

    def test_dea_most_efficient_branch_gets_score_1(self):
        inputs = [[10], [20]]
        outputs = [[100], [50]]
        from src.application.services.dea_service import DEAService
        service = DEAService()
        scores = service.calculate_efficiency(inputs, outputs)
        assert max(scores) == 1.0

    def test_dea_raises_error_on_empty_input(self):
        from src.application.services.dea_service import DEAService
        service = DEAService()
        with pytest.raises(ValueError):
            service.calculate_efficiency([], [])