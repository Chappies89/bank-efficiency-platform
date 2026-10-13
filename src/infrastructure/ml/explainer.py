"""SHAP explainer wrapper.

Wraps the SHAP library so the application layer doesn't depend on it
directly. Uses TreeExplainer, which is the fast path for XGBoost models.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import shap

from src.application.services.ml_service import TrainedModel


class ShapExplainer:
    """Computes SHAP values for a trained tree-based model."""

    def explain(
        self,
        model: TrainedModel,
        features: pd.DataFrame,
    ) -> np.ndarray[Any, np.dtype[np.float64]]:
        """Return SHAP values for each feature.

        Args:
            model: A TrainedModel containing an XGBoost estimator.
            features: N x M DataFrame of operational KPIs.

        Returns:
            An (N, M) numpy array of SHAP values.

        Raises:
            ValueError: If features are empty.
        """
        if features.empty:
            raise ValueError("Features cannot be empty")

        if model.feature_names:
            features = features[model.feature_names]

        explainer = shap.TreeExplainer(model.model)
        shap_values = explainer.shap_values(features)

        return np.asarray(shap_values, dtype=np.float64)
