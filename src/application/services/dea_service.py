# ruff: noqa: N803, N806
"""DEA (Data Envelopment Analysis) service.

Computes relative efficiency scores for a set of Decision-Making Units
(DMUs) — in this case, bank branches.

The DEA model used is the input-oriented CCR model (Charnes, Cooper,
Rhodes, 1978) with constant returns to scale.

For each branch i, we solve:

    minimize    theta
    subject to  X * lambda  <= theta * x_i    (inputs)
                Y * lambda  >= y_i            (outputs)
                lambda      >= 0

The theta value is the efficiency score. theta = 1.0 means the branch
is on the efficiency frontier. theta < 1.0 means the branch could
reduce inputs by (1 - theta) * 100% and still produce the same outputs.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import linprog

from src.domain.value_objects.efficiency_score import EfficiencyScore

# Type alias for a 2D float64 matrix — used throughout the DEA LP.
FloatMatrix = np.ndarray[tuple[int, int], np.dtype[np.float64]]


class DEAService:
    """Computes DEA efficiency scores using linear programming."""

    def calculate_efficiency(
        self,
        inputs: list[list[float]],
        outputs: list[list[float]],
    ) -> list[EfficiencyScore]:
        """Compute efficiency scores for all DMUs.

        Args:
            inputs: N x M matrix where N is the number of DMUs and M the
                number of input variables (e.g. FTE, opex, sqm).
            outputs: N x S matrix where S is the number of output variables
                (e.g. deposits, loans, new accounts).

        Returns:
            A list of EfficiencyScore objects, one per DMU.

        Raises:
            ValueError: If inputs or outputs are empty, or if shapes mismatch.
        """
        if not inputs or not outputs:
            raise ValueError("Inputs and outputs cannot be empty")

        X = np.array(inputs, dtype=float)
        Y = np.array(outputs, dtype=float)

        if X.ndim != 2 or Y.ndim != 2:
            raise ValueError("Inputs and outputs must be 2D matrices")

        if X.shape[0] != Y.shape[0]:
            raise ValueError(
                f"Number of DMUs must match: got {X.shape[0]} inputs " f"and {Y.shape[0]} outputs"
            )

        n_dmus = X.shape[0]
        scores: list[EfficiencyScore] = []
        for i in range(n_dmus):
            theta = self._solve_lp(X, Y, i)
            scores.append(EfficiencyScore(theta))
        return scores

    def _solve_lp(
        self,
        X: FloatMatrix,
        Y: FloatMatrix,
        i: int,
    ) -> float:
        """Solve the CCR DEA linear program for DMU i.

        Input-oriented formulation:
            minimize    theta
            subject to  X @ lambda  <= theta * x_i    (inputs)
                        Y @ lambda  >= y_i            (outputs)
                        lambda      >= 0
                        theta       >= 0

        Rewritten for scipy.optimize.linprog (A_ub @ x <= b_ub):
            [-x_i,  X] @ [theta; lambda]  <= 0      (inputs)
            [ 0,  -Y] @ [theta; lambda]  <= -y_i    (outputs)
        """
        n = X.shape[0]
        m = X.shape[1]
        s = Y.shape[1]

        # Variables: [theta, lambda_1, ..., lambda_n]
        # Objective: minimize theta
        c = np.concatenate([[1.0], np.zeros(n)])

        # Constraint 1: -theta * x_i + X @ lambda <= 0
        A_ub_top = np.hstack([-X[i : i + 1].T, X.T])  # shape (m, 1 + n)

        # Constraint 2: -Y @ lambda <= -y_i
        A_ub_bot = np.hstack([np.zeros((s, 1)), -Y.T])  # shape (s, 1 + n)

        A_ub = np.vstack([A_ub_top, A_ub_bot])
        b_ub = np.concatenate([np.zeros(m), -Y[i]])

        # Bounds: theta >= 0, lambda >= 0
        bounds = [(0.0, None)] * (1 + n)

        result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

        if not result.success:
            raise RuntimeError(f"LP solver failed for DMU {i}: {result.message}")

        # theta is the first variable; clamp to [0, 1] for float safety
        theta = float(result.x[0])
        return min(max(theta, 0.0), 1.0)
