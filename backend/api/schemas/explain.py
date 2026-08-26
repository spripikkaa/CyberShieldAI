from typing import Literal

from pydantic import BaseModel, Field


class FeatureContribution(BaseModel):
    """Single feature contribution toward the model prediction."""

    feature: str = Field(..., description="Feature name from the PhiUSIIL schema.")
    feature_value: float = Field(..., description="Input value supplied for this feature.")
    shap_value: float = Field(..., description="SHAP contribution for the predicted class.")
    impact: Literal["toward_phishing", "toward_legitimate", "neutral"] = Field(
        ...,
        description="Directional effect of this feature on the prediction.",
    )


class ExplainResponse(BaseModel):
    """SHAP-based explanation for a phishing classification."""

    prediction: Literal["Legitimate", "Phishing"] = Field(
        ...,
        description="Final model classification.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence for the predicted class.",
    )
    top_10_important_features: list[FeatureContribution] = Field(
        ...,
        description="Top 10 features ranked by absolute SHAP value for this prediction.",
    )
    shap_values: dict[str, float] = Field(
        ...,
        description="Per-feature SHAP values for the predicted class.",
    )
    feature_importance: dict[str, float] = Field(
        ...,
        description="Global Random Forest feature importances from the trained model.",
    )
    explanation: str = Field(
        ...,
        description="Plain-English summary of why the URL was classified this way.",
    )
