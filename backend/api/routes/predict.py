import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status

from backend.api.schemas.predict import PredictResponse
from backend.cybersecurity.exceptions import InvalidDomainError
from backend.exceptions import (
    FeatureExtractionError,
    FeatureMismatchError,
    ModelNotLoadedError,
    PredictionError,
    model_not_loaded_message,
)
from backend.ml.feature_extractor import extract_features_from_url
from backend.ml.predictor import predict_phishing
from backend.services.scan_persistence import persist_scan_report_if_connected

logger = logging.getLogger(__name__)

router = APIRouter(tags=["prediction"])


@router.get(
    "/predict",
    response_model=PredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Classify a website URL as Legitimate or Phishing",
)
def predict(
    background_tasks: BackgroundTasks,
    url: str = Query(
        ...,
        min_length=3,
        description="Website URL to analyze (e.g. https://example.com).",
        examples=["https://example.com"],
    ),
    user_id: str | None = Query(
        None,
        min_length=1,
        description="Optional user id. When provided, the scan is saved to ScanReports.",
    ),
) -> PredictResponse:
    """
    Extract features from the provided URL and return a phishing classification.

    Features are computed automatically using the URL feature extraction pipeline
before XGBoost inference.
    """
    try:
        features = extract_features_from_url(url)
        prediction, confidence = predict_phishing(features)
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
        logger.error("Model file missing during prediction request")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=model_not_loaded_message(),
        ) from exc
    except ModelNotLoadedError as exc:
        logger.error("Model not loaded during prediction request")
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
        logger.exception("Prediction pipeline failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    if user_id:
        background_tasks.add_task(
            persist_scan_report_if_connected,
            user_id,
            url,
            prediction,
            confidence,
        )

    return PredictResponse(prediction=prediction, confidence=confidence)
