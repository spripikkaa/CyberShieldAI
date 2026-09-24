from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = PROJECT_ROOT / "model"
MODEL_FILENAME = "phishing_url_model.pkl"


def get_model_path() -> Path:
    return MODEL_DIR / MODEL_FILENAME