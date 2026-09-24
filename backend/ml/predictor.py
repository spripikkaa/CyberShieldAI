import logging
from typing import Any

import numpy as np
import pandas as pd

from backend.exceptions import FeatureMismatchError, PredictionError
from backend.ml.features import FEATURE_NAMES, LABEL_TO_CLASS
from backend.ml.loader import get_phishing_model

logger = logging.getLogger(__name__)


def _resolve_feature_order(model: Any) -> list[str]:
    """Use the model's saved feature order when available."""
    model_features = getattr(model, "feature_names_in_", None)

    if model_features is not None:
        return [str(name) for name in model_features]

    return FEATURE_NAMES


def validate_feature_order(model: Any) -> None:
    """Ensure API feature schema matches the trained XGBoost model."""
    model_features = getattr(model, "feature_names_in_", None)

    if model_features is None:
        return

    expected = [str(name) for name in model_features]

    if expected != FEATURE_NAMES:
        raise FeatureMismatchError(
            "Configured FEATURE_NAMES do not match the trained XGBoost model's "
            "feature_names_in_."
        )


def predict_phishing(features: dict[str, float]) -> tuple[str, float]:
    """
    Run XGBoost inference on extracted URL features.

    Returns:
        A tuple of (prediction_label, confidence_score).
    """

    model = get_phishing_model()

    validate_feature_order(model)

    feature_order = _resolve_feature_order(model)

    feature_vector = pd.DataFrame(
        [[features[name] for name in feature_order]],
        columns=feature_order,
    )

    try:
        predicted_class = int(
            model.predict(feature_vector)[0]
        )

        probabilities = model.predict_proba(
            feature_vector
        )[0]

        confidence = float(
            np.max(probabilities)
        )

    except Exception as exc:
        logger.exception("XGBoost model inference failed")

        raise PredictionError(
            "Failed to generate prediction."
        ) from exc

    label = LABEL_TO_CLASS.get(
        predicted_class
    )

    if label is None:
        raise PredictionError(
            f"Model returned an unknown class label: {predicted_class}"
        )

    return label, round(confidence, 4)