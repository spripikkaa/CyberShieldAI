from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from backend.ml.url_feature_extractor import (
    FEATURE_NAMES,
    extract_url_features,
)


PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "model" / "phishing_url_model.pkl"
LEGITIMATE_URLS_PATH = PROJECT_ROOT / "dataset" / "legitimate_urls.csv"

# All URLs in legitimate_urls.csv are expected to be Legitimate (label=1).
EXPECTED_LABEL = "Legitimate"
EXPECTED_CLASS = 1


model = joblib.load(MODEL_PATH)

print("\nMODEL LOADED SUCCESSFULLY")
print("Model type:", type(model))
print("Number of model features:", len(model.feature_names_in_))

if list(model.feature_names_in_) != FEATURE_NAMES:
    print("\nERROR: Feature order mismatch!")
    print("\nExtractor features:")
    print(FEATURE_NAMES)
    print("\nModel features:")
    print(list(model.feature_names_in_))
    raise SystemExit(1)

print("\nFEATURE ORDER VERIFIED")
print("48 model features = 48 extractor features")

if not LEGITIMATE_URLS_PATH.is_file():
    print(f"\nERROR: Test set not found at {LEGITIMATE_URLS_PATH}")
    raise SystemExit(1)

test_df = pd.read_csv(LEGITIMATE_URLS_PATH)

if "URL" not in test_df.columns:
    print("\nERROR: legitimate_urls.csv must contain a URL column.")
    raise SystemExit(1)

test_urls = (
    test_df["URL"]
    .dropna()
    .astype(str)
    .str.strip()
)
test_urls = test_urls[test_urls.str.len() > 0].tolist()

print(f"\nTest set: {LEGITIMATE_URLS_PATH}")
print(f"Expected label for all URLs: {EXPECTED_LABEL}")


def predict_url(url: str) -> tuple[int, str, float]:
    features = extract_url_features(url)

    feature_vector = np.array(
        [
            [
                features[name]
                for name in model.feature_names_in_
            ]
        ],
        dtype=np.float32,
    )

    prediction = int(model.predict(feature_vector)[0])
    probabilities = model.predict_proba(feature_vector)[0]
    confidence = float(np.max(probabilities)) * 100
    label = "Legitimate" if prediction == 1 else "Phishing"

    return prediction, label, confidence


legitimate_predictions = 0
phishing_predictions = 0
misclassified: list[tuple[str, str, float]] = []
errors: list[tuple[str, str]] = []

for url in test_urls:
    try:
        prediction, label, confidence = predict_url(url)

        if prediction == EXPECTED_CLASS:
            legitimate_predictions += 1
        else:
            phishing_predictions += 1
            misclassified.append((url, label, confidence))

    except Exception as exc:
        errors.append((url, repr(exc)))

total_urls = len(test_urls)
correct_predictions = legitimate_predictions
accuracy = (correct_predictions / total_urls * 100) if total_urls else 0.0

print("\n" + "=" * 70)
print("LEGITIMATE URL TEST RESULTS")
print("=" * 70)
print(f"Total URLs             : {total_urls}")
print(f"Legitimate predictions : {legitimate_predictions}")
print(f"Phishing predictions   : {phishing_predictions}")
print(f"Accuracy               : {accuracy:.2f}%")

if misclassified:
    print("\n" + "=" * 70)
    print("MISCLASSIFIED URLS")
    print("=" * 70)

    for url, label, confidence in misclassified:
        print(f"{url}")
        print(f"  Prediction : {label}")
        print(f"  Confidence : {confidence:.2f}%")
        print()
else:
    print("\nNo misclassified URLs.")

if errors:
    print("\n" + "=" * 70)
    print("ERRORS")
    print("=" * 70)

    for url, message in errors:
        print(f"{url}")
        print(f"  Error: {message}")
        print()
