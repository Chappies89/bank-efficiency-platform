"""SHAP explainability service.

Orchestrates SHAP computation and formats results as ranked
feature contributions for a single prediction.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.application.services.ml_service import TrainedModel


@dataclass(frozen=True)
class FeatureContribution:
    """A single feature's contribution to a prediction.

    Attributes:
        feature: The feature name.
        contribution: How much this feature pushed the score (positive or negative).
        value: The feature's actual value for this prediction.
    """

    feature: str
    contribution: float
    value: float


class ShapService:
    """Explains ML predictions using SHAP values."""

    def explain(
        self,
        model: TrainedModel,
        features: pd.DataFrame,
        top_n: int = 5,
    ) -> list[FeatureContribution]:
        """Explain a single prediction.

        Args:
            model: A trained model.
            features: A single-row DataFrame of operational KPIs.
            top_n: Return this many top contributions (by absolute magnitude).

        Returns:
            A ranked list of FeatureContribution objects.

        Raises:
            ValueError: If features are empty or contain more than one row.
        """
        from src.infrastructure.ml.explainer import ShapExplainer

        if features.empty:
            raise ValueError("Features cannot be empty")
        if len(features) > 1:
            raise ValueError("Explanation is for a single prediction at a time")

        if model.feature_names:
            features = features[model.feature_names]

        shap_values = ShapExplainer().explain(model, features)[0]

        contributions = [
            FeatureContribution(
                feature=str(col),
                contribution=float(shap_values[i]),
                value=float(features.iloc[0, i]),
            )
            for i, col in enumerate(features.columns)
        ]

        # Sort by absolute magnitude; keep the strongest drivers
        contributions.sort(key=lambda c: abs(c.contribution), reverse=True)
        return contributions[:top_n]
