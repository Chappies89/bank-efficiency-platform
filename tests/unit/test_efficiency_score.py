"""Unit tests for the EfficiencyScore value object.

This is a TDD test. It will FAIL until we implement the EfficiencyScore class.
"""
import pytest

from src.domain.value_objects.efficiency_score import EfficiencyScore


class TestEfficiencyScore:
    """Test suite for EfficiencyScore value object."""

    def test_efficiency_score_accepts_value_between_0_and_1(self):
        """A valid efficiency score is between 0.0 and 1.0 inclusive."""
        score = EfficiencyScore(0.85)
        assert score.value == 0.85

    def test_efficiency_score_accepts_boundary_value_0(self):
        """0.0 is a valid efficiency score (fully inefficient)."""
        score = EfficiencyScore(0.0)
        assert score.value == 0.0

    def test_efficiency_score_accepts_boundary_value_1(self):
        """1.0 is a valid efficiency score (fully efficient)."""
        score = EfficiencyScore(1.0)
        assert score.value == 1.0

    def test_efficiency_score_rejects_value_below_0(self):
        """Negative values must raise ValueError."""
        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            EfficiencyScore(-0.1)

    def test_efficiency_score_rejects_value_above_1(self):
        """Values above 1.0 must raise ValueError."""
        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            EfficiencyScore(1.1)

    def test_efficiency_score_is_immutable(self):
        """EfficiencyScore is a value object and must be immutable."""
        score = EfficiencyScore(0.75)
        with pytest.raises(AttributeError):
            score.value = 0.5

    def test_efficiency_score_equality(self):
        """Two scores with the same value must be equal."""
        assert EfficiencyScore(0.5) == EfficiencyScore(0.5)

    def test_efficiency_score_inequality(self):
        """Two scores with different values must not be equal."""
        assert EfficiencyScore(0.5) != EfficiencyScore(0.6)

    def test_efficiency_score_rejects_non_numeric_input(self):
        """Non-numeric values must raise ValueError."""
        with pytest.raises(ValueError, match="must be numeric"):
            EfficiencyScore("0.5")

    def test_is_efficient_returns_true_when_value_is_1(self):
        """is_efficient() returns True only when value is exactly 1.0."""
        assert EfficiencyScore(1.0).is_efficient() is True
        assert EfficiencyScore(0.99).is_efficient() is False

    def test_is_inefficient_returns_true_when_value_below_1(self):
        """is_inefficient() returns True when value < 1.0."""
        assert EfficiencyScore(0.5).is_inefficient() is True
        assert EfficiencyScore(1.0).is_inefficient() is False

    def test_repr_returns_readable_format(self):
        """__repr__ should return a readable string showing the field name."""
        assert repr(EfficiencyScore(0.75)) == "EfficiencyScore(value=0.75)"