from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.ml.feature_extractor import extract_features_from_url
from backend.ml.predictor import predict_phishing


app = FastAPI(
    title="CyberShield AI",
    description="AI-based phishing website detection and cybersecurity assistant",
    version="1.0"
)


class URLRequest(BaseModel):
    url: str


@app.get("/")
def home():
    return {
        "message": "CyberShield AI Backend Running Successfully"
    }


@app.post("/predict")
def predict(request: URLRequest):
    try:
        # Extract URL features
        features = extract_features_from_url(request.url)

        # Predict using ML model
        label, confidence = predict_phishing(features)

        return {
            "url": request.url,
            "prediction": label,
            "confidence": confidence
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )