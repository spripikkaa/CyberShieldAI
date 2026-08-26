"""Custom exceptions for ML prediction failures."""


class ModelNotLoadedError(Exception):
    """Raised when the phishing model file is missing or failed to load."""


class FeatureMismatchError(Exception):
    """Raised when request features do not match the trained model's expectations."""


class PredictionError(Exception):
    """Raised when inference fails unexpectedly."""


class ExplainError(Exception):
    """Raised when SHAP explanation generation fails."""


class FeatureExtractionError(Exception):
    """Raised when features cannot be extracted from the supplied URL."""


def model_not_loaded_message() -> str:
    from backend.ml.paths import get_model_path

    return (
        f"Phishing model is unavailable. Ensure phishing_model.pkl exists at "
        f"{get_model_path()}."
    )
