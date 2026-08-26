import logging
from typing import Any

import numpy as np

from backend.exceptions import FeatureMismatchError
from backend.ml.features import FEATURE_NAMES, LABEL_TO_CLASS
from backend.ml.loader import get_phishing_model

logger = logging.getLogger(__name__)


def validate_feature_order(model: Any) -> None:
    """
    Make sure the loaded XGBoost model uses the same
    48-feature order as the URL-only feature extractor.
    """

    model_features = list(
        getattr(model, "feature_names_in_", [])
    )

    expected_features = list(FEATURE_NAMES)

    if not model_features:
        raise FeatureMismatchError(
            "Loaded model does not contain feature_names_in_."
        )

    if model_features != expected_features:
        raise FeatureMismatchError(
            "Model feature order does not match the "
            "URL-only feature schema.\n"
            f"Expected: {expected_features}\n"
            f"Model has: {model_features}"
        )


def _prepare_features(
    features: dict[str, float],
) -> np.ndarray:
    """
    Convert the 48 URL features into the exact order
    expected by the trained XGBoost model.
    """

    missing = [
        name
        for name in FEATURE_NAMES
        if name not in features
    ]

    if missing:
        raise FeatureMismatchError(
            f"Missing features: {missing}"
        )

    values = [
        float(features[name])
        for name in FEATURE_NAMES
    ]

    return np.asarray(
        [values],
        dtype=np.float32,
    )


def predict_phishing(
    features: dict[str, float],
) -> tuple[str, float]:
    """
    Predict whether a URL is phishing or legitimate.

    Returns:
        (prediction_label, confidence)
    """

    model = get_phishing_model()

    # Verify that the model and extractor use
    # exactly the same 48 features.
    validate_feature_order(model)

    X = _prepare_features(features)

    # Raw prediction:
    # 0 = Phishing
    # 1 = Legitimate
    prediction = int(
        model.predict(X)[0]
    )

    # Probability for each class.
    probabilities = model.predict_proba(X)[0]

    confidence = float(
        probabilities[prediction]
    )

    label = LABEL_TO_CLASS.get(
        prediction,
        "Unknown",
    )

    logger.info(
        "Prediction: %s | Confidence: %.4f",
        label,
        confidence,
    )

    return (
        label,
        round(confidence, 4),
    )