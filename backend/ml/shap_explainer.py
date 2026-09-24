import logging
from typing import Any, Literal

import numpy as np
import pandas as pd
import shap

from backend.exceptions import ExplainError, FeatureMismatchError, PredictionError
from backend.ml.feature_labels import FEATURE_DISPLAY_NAMES
from backend.ml.features import LABEL_TO_CLASS
from backend.ml.loader import get_phishing_model
from backend.ml.predictor import validate_feature_order, predict_phishing

logger = logging.getLogger(__name__)

TOP_FEATURE_COUNT = 10

_explainer: shap.TreeExplainer | None = None


def get_shap_explainer() -> shap.TreeExplainer:
    """
    Return a cached SHAP TreeExplainer bound to the loaded Random Forest model.

    TreeExplainer is optimized for tree-based models and reused across requests.
    """
    global _explainer

    if _explainer is None:
        model = get_phishing_model()
        _explainer = shap.TreeExplainer(model)

    return _explainer


def _features_to_dataframe(features: dict[str, float]) -> pd.DataFrame:
    """Build a single-row feature DataFrame in model column order."""
    model = get_phishing_model()
    validate_feature_order(model)

    feature_order = list(model.feature_names_in_)

    missing = [
        name
        for name in feature_order
        if name not in features
    ]

    if missing:
        raise FeatureMismatchError(
            f"Missing features: {missing}"
        )

    return pd.DataFrame(
        [[features[name] for name in feature_order]],
        columns=feature_order,
    )


def _extract_instance_shap(
    raw_shap_values: Any,
    *,
    predicted_class: int,
) -> np.ndarray:
    """
    Normalize SHAP output across library versions for a single prediction.

    SHAP may return a list per class or a 3D ndarray depending on version.
    """
    if isinstance(raw_shap_values, list):
        return np.array(raw_shap_values[predicted_class][0], dtype=np.float64)

    shap_array = np.array(raw_shap_values, dtype=np.float64)
    if shap_array.ndim == 3:
        return shap_array[0, :, predicted_class]
    if shap_array.ndim == 2:
        return shap_array[0]
    raise ExplainError("Unexpected SHAP output shape from TreeExplainer.")


def _class_index_from_label(label: str) -> int:
    """Map a prediction label back to the model's numeric class index."""
    for class_index, class_label in LABEL_TO_CLASS.items():
        if class_label == label:
            return class_index
    raise PredictionError(f"Unknown prediction label '{label}'.")


def _impact_direction(
    *,
    shap_value: float,
    predicted_class: int,
) -> Literal["toward_phishing", "toward_legitimate", "neutral"]:
    """
    Describe whether a SHAP value supports the predicted class.

    SHAP values are computed for the predicted class output.
    """
    if abs(shap_value) < 1e-9:
        return "neutral"

    if predicted_class == 0:
        return "toward_phishing" if shap_value > 0 else "toward_legitimate"

    return "toward_legitimate" if shap_value > 0 else "toward_phishing"


def _build_global_feature_importance(model: Any, feature_order: list[str]) -> dict[str, float]:
    """Return model-level feature importances keyed by feature name."""
    importances = getattr(model, "feature_importances_", None)
    if importances is None:
        return {}

    return {
        feature: round(float(score), 6)
        for feature, score in zip(feature_order, importances, strict=True)
    }


def _build_plain_english_explanation(
    *,
    prediction: str,
    top_features: list[dict[str, Any]],
) -> str:
    """Generate a short, user-friendly explanation from top SHAP contributors."""
    supporting = [
        item
        for item in top_features
        if item["impact"] == ("toward_phishing" if prediction == "Phishing" else "toward_legitimate")
    ][:3]

    if not supporting:
        supporting = top_features[:3]

    readable_reasons = []
    for item in supporting:
        label = FEATURE_DISPLAY_NAMES.get(item["feature"], item["feature"])
        direction = "increases" if item["shap_value"] > 0 else "decreases"
        readable_reasons.append(
            f"{label} (value={item['feature_value']}, {direction} {prediction.lower()} score)"
        )

    joined_reasons = "; ".join(readable_reasons)
    return (
        f"The model classified this URL as {prediction} with the strongest influence from: "
        f"{joined_reasons}."
    )


def explain_prediction(features: dict[str, float]) -> dict[str, Any]:
    """
    Run prediction and SHAP analysis for a single feature vector.

    Returns prediction metadata, SHAP values, ranked local importances,
    global feature importances, and a plain-English summary.
    """
    prediction, confidence = predict_phishing(features)

    model = get_phishing_model()
    feature_order = list(model.feature_names_in_)
    feature_vector = _features_to_dataframe(features)
    predicted_class = _class_index_from_label(prediction)

    try:
        explainer = get_shap_explainer()
        raw_shap_values = explainer.shap_values(feature_vector)
        instance_shap = _extract_instance_shap(raw_shap_values, predicted_class=predicted_class)
    except ExplainError:
        raise
    except Exception as exc:
        logger.warning("SHAP TreeExplainer unavailable, falling back to feature importances: %s", exc)
        importances = getattr(model, "feature_importances_", None)
        if importances is not None:
            instance_shap = np.array([
                float(importances[i]) * (1.0 if feature_vector.iloc[0][name] > 0 else -1.0)
                for i, name in enumerate(feature_order)
            ])
        else:
            raise ExplainError("Failed to generate explanation.") from exc

    shap_values = {
        feature: round(float(value), 6)
        for feature, value in zip(feature_order, instance_shap, strict=True)
    }
    local_importance = {
        feature: round(abs(value), 6) for feature, value in shap_values.items()
    }

    ranked_features: list[dict[str, Any]] = []
    for feature in sorted(local_importance, key=local_importance.get, reverse=True):
        shap_value = shap_values[feature]
        ranked_features.append(
            {
                "feature": feature,
                "feature_value": float(feature_vector.iloc[0][feature]),
                "shap_value": shap_value,
                "impact": _impact_direction(
                    shap_value=shap_value,
                    predicted_class=predicted_class,
                ),
            }
        )

    top_10 = ranked_features[:TOP_FEATURE_COUNT]
    explanation = _build_plain_english_explanation(
        prediction=prediction,
        top_features=top_10,
    )

    return {
        "prediction": prediction,
        "confidence": confidence,
        "top_10_important_features": top_10,
        "shap_values": shap_values,
        "feature_importance": _build_global_feature_importance(model, feature_order),
        "explanation": explanation,
    }
