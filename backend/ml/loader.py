from typing import Any

import joblib

from backend.ml.paths import get_model_path

_model: Any | None = None


def load_phishing_model(*, force_reload: bool = False) -> Any:
    """Load the URL-only phishing detection model from disk."""

    global _model

    if _model is not None and not force_reload:
        return _model

    model_path = get_model_path()

    if not model_path.is_file():
        raise FileNotFoundError(
            f"Phishing model not found at {model_path}"
        )

    _model = joblib.load(model_path)

    return _model


def get_phishing_model() -> Any:
    """Return the cached phishing model."""

    return load_phishing_model()