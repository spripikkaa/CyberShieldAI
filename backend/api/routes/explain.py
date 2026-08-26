import logging

from fastapi import APIRouter, HTTPException, Query, status

from backend.api.schemas.explain import ExplainResponse
from backend.cybersecurity.exceptions import InvalidDomainError
from backend.exceptions import (
    ExplainError,
    FeatureExtractionError,
    FeatureMismatchError,
    ModelNotLoadedError,
    PredictionError,
    model_not_loaded_message,
)
from backend.ml.feature_extractor import extract_features_from_url
from backend.ml.shap_explainer import explain_prediction

logger = logging.getLogger(__name__)

router = APIRouter(tags=["explainability"])


@router.get(
    "/explain",
    response_model=ExplainResponse,
    status_code=status.HTTP_200_OK,
    summary="Explain a phishing prediction with SHAP for a website URL",
)
def explain(
    url: str = Query(
        ...,
        min_length=3,
        description="Website URL to analyze (e.g. https://example.com).",
        examples=["https://example.com"],
    ),
) -> ExplainResponse:
    """
    Extract features from the URL, classify it, and return a SHAP-based explanation.

    Adds per-feature SHAP values, ranked local importances, global feature importance,
    and a plain-English summary on top of the prediction.
    """
    try:
        features = extract_features_from_url(url)
        result = explain_prediction(features)
    except InvalidDomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except FeatureExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except FileNotFoundError as exc:
        logger.error("Model file missing during explain request")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=model_not_loaded_message(),
        ) from exc
    except ModelNotLoadedError as exc:
        logger.error("Model not loaded during explain request")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except FeatureMismatchError as exc:
        logger.error("Feature schema mismatch with trained model")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except PredictionError as exc:
        logger.exception("Prediction step failed during explain request")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except ExplainError as exc:
        logger.exception("SHAP explanation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return ExplainResponse(**result)
