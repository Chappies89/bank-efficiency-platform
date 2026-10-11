"""Edge case tests for DEAService to achieve 100% coverage."""
from unittest.mock import patch

import numpy as np
import pytest

from src.application.services.dea_service import DEAService


class TestDEAServiceLpFailure:
    """Test the RuntimeError path when scipy.linprog fails."""

    def test_lp_failure_raises_runtime_error(self):
        service = DEAService()
        inputs = [[10.0], [20.0]]
        outputs = [[100.0], [200.0]]

        with patch(
            "src.application.services.dea_service.linprog"
        ) as mock_linprog:
            mock_result = type(
                "Result",
                (),
                {"success": False, "message": "Simulated LP failure"},
            )()
            mock_linprog.return_value = mock_result

            with pytest.raises(RuntimeError, match="LP solver failed"):
                service.calculate_efficiency(inputs, outputs)


class TestDEAServiceClamping:
    """Test the clamping branch when theta > 1 or < 0."""

    def test_theta_above_1_is_clamped_to_1(self):
        service = DEAService()
        inputs = [[10.0], [20.0]]
        outputs = [[100.0], [200.0]]

        with patch(
            "src.application.services.dea_service.linprog"
        ) as mock_linprog:
            mock_result = type(
                "Result",
                (),
                {
                    "success": True,
                    "x": np.array([1.5, 0.0, 0.0]),
                    "message": "ok",
                },
            )()
            mock_linprog.return_value = mock_result

            scores = service.calculate_efficiency(inputs, outputs)
            assert all(s.value <= 1.0 for s in scores)

    def test_negative_theta_is_clamped_to_0(self):
        service = DEAService()
        inputs = [[10.0], [20.0]]
        outputs = [[100.0], [200.0]]

        with patch(
            "src.application.services.dea_service.linprog"
        ) as mock_linprog:
            mock_result = type(
                "Result",
                (),
                {
                    "success": True,
                    "x": np.array([-0.5, 0.0, 0.0]),
                    "message": "ok",
                },
            )()
            mock_linprog.return_value = mock_result

            scores = service.calculate_efficiency(inputs, outputs)
            assert all(s.value >= 0.0 for s in scores)
