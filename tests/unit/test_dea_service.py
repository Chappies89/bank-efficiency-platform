"""Unit tests for the DEA service."""
import pytest

from src.application.services.dea_service import DEAService
from src.domain.value_objects.efficiency_score import EfficiencyScore


class TestDEAService:
    """Test suite for DEAService."""

    def setup_method(self) -> None:
        """Create a fresh service for each test."""
        self.service = DEAService()

    def test_dea_returns_one_score_per_dmu(self):
        """Number of returned scores equals number of DMUs."""
        inputs = [[10, 1000], [20, 2000], [15, 1500]]
        outputs = [[100], [200], [150]]
        scores = self.service.calculate_efficiency(inputs, outputs)
        assert len(scores) == 3
        assert all(isinstance(s, EfficiencyScore) for s in scores)

    def test_dea_scores_are_between_0_and_1(self):
        """All efficiency scores are in the valid [0, 1] range."""
        inputs = [[10, 1000], [20, 2000], [15, 1500]]
        outputs = [[100], [200], [150]]
        scores = self.service.calculate_efficiency(inputs, outputs)
        for score in scores:
            assert 0.0 <= score.value <= 1.0

    def test_most_efficient_dmu_gets_score_1(self):
        """The best performer receives an efficiency score of 1.0."""
        # DMU 1 is clearly the most efficient: uses 1 unit of input,
        # produces 10 units of output. DMUs 2 and 3 are dominated.
        inputs = [[1.0], [2.0], [3.0]]
        outputs = [[10.0], [15.0], [18.0]]
        scores = self.service.calculate_efficiency(inputs, outputs)
        assert scores[0].value == pytest.approx(1.0)

    def test_identical_dmus_are_all_efficient(self):
        """If all DMUs are identical, all should be efficient."""
        inputs = [[10.0], [10.0], [10.0]]
        outputs = [[100.0], [100.0], [100.0]]
        scores = self.service.calculate_efficiency(inputs, outputs)
        for score in scores:
            assert score.value == pytest.approx(1.0)

    def test_inefficient_dmu_gets_score_less_than_1(self):
        """A dominated DMU must receive a score strictly less than 1.0."""
        # DMU 3 uses the most input but produces the least output.
        inputs = [[5.0], [10.0], [20.0]]
        outputs = [[50.0], [60.0], [55.0]]
        scores = self.service.calculate_efficiency(inputs, outputs)
        assert scores[2].value < 1.0

    def test_raises_on_empty_inputs(self):
        """Empty inputs must raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            self.service.calculate_efficiency([], [[1.0]])

    def test_raises_on_empty_outputs(self):
        """Empty outputs must raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            self.service.calculate_efficiency([[1.0]], [])

    def test_raises_when_dmu_counts_mismatch(self):
        """Mismatched number of inputs and outputs must raise ValueError."""
        with pytest.raises(ValueError, match="must match"):
            self.service.calculate_efficiency(
                [[1.0], [2.0]],
                [[10.0], [20.0], [30.0]],
            )

    def test_multi_input_multi_output(self):
        """Service handles multiple inputs and outputs correctly."""
        # 4 DMUs, 2 inputs, 2 outputs.
        inputs = [
            [10.0, 100.0],
            [20.0, 200.0],
            [30.0, 300.0],
            [40.0, 400.0],
        ]
        outputs = [
            [100.0, 50.0],
            [180.0, 90.0],
            [210.0, 100.0],
            [250.0, 120.0],
        ]
        scores = self.service.calculate_efficiency(inputs, outputs)
        assert len(scores) == 4
        for score in scores:
            assert 0.0 <= score.value <= 1.0
