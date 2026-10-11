"""Model predictor — loads a trained model and generates predictions."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.application.services.ml_service import TrainedModel


class ModelPredictor:
    """Generates predictions from a TrainedModel."""

    def predict(
        self,
        model: TrainedModel,
        features: pd.DataFrame,
    ) -> np.ndarray:
        """Return raw predictions from the underlying estimator."""
        if model.feature_names:
            missing = set(model.feature_names) - set(features.columns)
            if missing:
                raise ValueError(
                    f"Features missing required columns: {sorted(missing)}"
                )
            features = features[model.feature_names]

        return model.model.predict(features)
