"""Model predictor — loads a trained model and generates predictions."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.application.services.ml_service import TrainedModel


class ModelPredictor:
    """Generates predictions from a TrainedModel."""

    def predict(
        self,
        model: TrainedModel,
        features: pd.DataFrame,
    ) -> np.ndarray[Any, np.dtype[np.float64]]:
        """Return raw predictions from the underlying estimator."""
        if model.feature_names:
            missing = set(model.feature_names) - set(features.columns)
            if missing:
                raise ValueError(
                    f"Features missing required columns: {sorted(missing)}"
                )
            features = features[model.feature_names]

        raw = model.model.predict(features)
        return np.asarray(raw, dtype=np.float64)
