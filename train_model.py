"""
CyberShield AI
URL-ONLY PHISHING DETECTION MODEL

Pipeline:

    URL
      ↓
    URL Feature Extractor
      ↓
    48 deterministic features
      ↓
    XGBoost
      ↓
    0 = Phishing
    1 = Legitimate
"""

import sys
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent

DATASET_PATH = (
    PROJECT_ROOT
    / "dataset"
    / "PhiUSIIL_Phishing_URL_Dataset.csv"
)

LEGITIMATE_URLS_PATH = (
    PROJECT_ROOT
    / "dataset"
    / "legitimate_urls.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "model"
)

MODEL_PATH = (
    MODEL_DIR
    / "phishing_url_model.pkl"
)


# ============================================================
# IMPORT URL FEATURE EXTRACTOR
# ============================================================

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)

from backend.ml.url_feature_extractor import (
    FEATURE_NAMES,
    extract_url_features,
)


# ============================================================
# SETTINGS
# ============================================================

RANDOM_STATE = 42

TEST_SIZE = 0.20


# ============================================================
# XGBOOST SETTINGS
# ============================================================

MODEL_PARAMS = {
    "n_estimators": 250,
    "max_depth": 5,
    "learning_rate": 0.05,
    "subsample": 0.80,
    "colsample_bytree": 0.80,

    "objective": "binary:logistic",
    "eval_metric": "logloss",

    "random_state": RANDOM_STATE,
    "n_jobs": -1,

    "tree_method": "hist",

    "min_child_weight": 3,
    "gamma": 0.1,

    "reg_alpha": 0.05,
    "reg_lambda": 1.5,
}


# ============================================================
# REAL-WORLD SANITY CHECK URLS
# ============================================================

LEGITIMATE_TEST_URLS = [
    "https://www.google.com",
    "https://www.amazon.in",
    "https://www.ajio.com",
    "https://www.myntra.com",
    "https://www.meesho.com",
    "https://www.facebook.com",
    "https://www.youtube.com",
    "https://www.wikipedia.org",
    "https://github.com",
    "https://openai.com",
    "https://chatgpt.com",
]


LEGITIMATE_APEX_TEST_URLS = [
    "https://github.com",
    "https://openai.com",
    "https://chatgpt.com",
    "https://cloud.google.com",
    "https://developers.google.com",
    "https://pytorch.org",
    "https://platform.openai.com",
    "https://huggingface.co",
]


PHISHING_TEST_URLS = [
    "http://google-account-verify.example.com/security/login",
    "http://paypal-login-security.example.com/verify",
    "http://amazon-account-check.example.com/login",
]


# ============================================================
# LEGITIMATE URL AUGMENTATION (debias has_www)
# ============================================================

def _normalize_training_url(url: str) -> str:
    normalized = str(url).strip()

    if not normalized:
        return ""

    if "://" not in normalized:
        normalized = "https://" + normalized

    return normalized


def _replace_hostname(url: str, hostname: str) -> str:
    normalized = _normalize_training_url(url)
    parsed = urlparse(normalized)

    if not parsed.hostname:
        return normalized

    port = f":{parsed.port}" if parsed.port else ""
    netloc = f"{hostname}{port}"

    return urlunparse(
        (
            parsed.scheme,
            netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
    )


def _legitimate_www_variants(url: str) -> list[str]:
    """
    Return both www and non-www forms of a legitimate URL so the model
    does not treat missing www as a phishing signal.
    """

    original = str(url).strip()
    normalized = _normalize_training_url(original)
    parsed = urlparse(normalized)
    hostname = parsed.hostname

    if not hostname:
        return [original] if original else []

    variants = {original, normalized}
    hostname_lower = hostname.lower()

    if hostname_lower.startswith("www."):
        apex = hostname_lower[4:]

        if apex:
            variants.add(
                _replace_hostname(
                    normalized,
                    apex,
                )
            )
    else:
        variants.add(
            _replace_hostname(
                normalized,
                f"www.{hostname_lower}",
            )
        )

    return sorted(variants)


def augment_legitimate_urls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Duplicate label=1 rows with www/apex variants to reduce has_www bias.
    """

    legitimate = df[df["label"] == 1]

    extra_rows = []

    for url in legitimate["URL"]:
        for variant in _legitimate_www_variants(url):
            extra_rows.append(
                {
                    "URL": variant,
                    "label": 1,
                }
            )

    if not extra_rows:
        return df

    augmented = pd.DataFrame(extra_rows)

    combined = pd.concat(
        [
            df,
            augmented,
        ],
        ignore_index=True,
    )

    combined = combined.drop_duplicates(
        subset=[
            "URL",
            "label",
        ]
    ).reset_index(
        drop=True
    )

    return combined


def _predict_url(
    model: XGBClassifier,
    url: str,
) -> tuple[int, float]:
    features = extract_url_features(url)

    values = np.array(
        [
            [
                features[name]
                for name in FEATURE_NAMES
            ]
        ],
        dtype=np.float32,
    )

    prediction = int(
        model.predict(values)[0]
    )

    probability = float(
        model.predict_proba(values)[0][1]
    )

    return prediction, probability


def _evaluate_urls(
    model: XGBClassifier,
    urls: list[str],
    expected_label: int,
) -> list[bool]:
    results = []

    for url in urls:
        try:
            prediction, probability = _predict_url(
                model,
                url,
            )

            passed = prediction == expected_label
            results.append(passed)

            label = (
                "Legitimate"
                if prediction == 1
                else "Phishing"
            )

            status = "PASS" if passed else "FAIL"

            print(
                f"{url:<65} -> "
                f"{label:<12} "
                f"P(legit)={probability:.4f}  "
                f"[{status}]"
            )

        except Exception as exc:
            results.append(False)

            print(
                f"{url:<65} -> "
                f"ERROR: {exc}  "
                f"[FAIL]"
            )

    return results


# ============================================================
# HEADER
# ============================================================

print()
print("=" * 70)
print("CYBERSHIELD AI - URL-ONLY XGBOOST TRAINING")
print("=" * 70)
print()


# ============================================================
# STEP 1 - CHECK DATASET
# ============================================================

print("[1/10] Checking dataset...")
print()

if not DATASET_PATH.is_file():

    print("ERROR: Dataset not found.")
    print()
    print("Expected:")
    print(DATASET_PATH)
    print()

    sys.exit(1)


print("Dataset:")
print(DATASET_PATH)


# ============================================================
# STEP 2 - LOAD DATASET
# ============================================================

print()
print("[2/10] Loading dataset...")
print()

df = pd.read_csv(
    DATASET_PATH
)

print(
    "Dataset shape:",
    df.shape,
)


required_columns = [
    "URL",
    "label",
]


for column in required_columns:

    if column not in df.columns:

        print(
            f"ERROR: Required column "
            f"'{column}' not found."
        )

        print()
        print(
            "Available columns:"
        )

        print(
            list(df.columns)
        )

        sys.exit(1)


# ============================================================
# LOAD ADDITIONAL LEGITIMATE URLs
# ============================================================

if LEGITIMATE_URLS_PATH.is_file():

    print()
    print(
        "Loading additional legitimate URLs..."
    )

    legitimate_df = pd.read_csv(
        LEGITIMATE_URLS_PATH
    )

    if "URL" not in legitimate_df.columns:

        print(
            "WARNING: legitimate_urls.csv "
            "does not contain a URL column."
        )

    else:

        legitimate_df = legitimate_df[
            ["URL"]
        ].copy()

        # 1 = Legitimate
        legitimate_df["label"] = 1

        print(
            "Additional legitimate URLs:",
            len(legitimate_df),
        )

        df = pd.concat(
            [
                df,
                legitimate_df,
            ],
            ignore_index=True,
        )

        print(
            "Combined dataset shape:",
            df.shape,
        )

else:

    print()
    print(
        "WARNING: legitimate_urls.csv "
        "not found."
    )


# ============================================================
# STEP 3 - CHECK LABELS
# ============================================================

print()
print("[3/10] Checking labels...")
print()

print(
    df["label"].value_counts()
)

print()
print("Label meaning:")
print("0 = Phishing")
print("1 = Legitimate")


# ============================================================
# STEP 4 - CLEAN DATA
# ============================================================

print()
print("[4/10] Cleaning URL data...")
print()

df = df[
    df["URL"].notna()
    & df["label"].notna()
].copy()


df["URL"] = (
    df["URL"]
    .astype(str)
    .str.strip()
)


df = df[
    df["URL"].str.len() > 0
].copy()


df["label"] = pd.to_numeric(
    df["label"],
    errors="coerce",
)


df = df[
    df["label"].isin([0, 1])
].copy()


df["label"] = (
    df["label"]
    .astype(int)
)


print(
    "Usable rows:",
    len(df),
)


# ============================================================
# REMOVE EXACT DUPLICATES
# ============================================================

before = len(df)

df = df.drop_duplicates(
    subset=[
        "URL",
        "label",
    ]
).reset_index(
    drop=True
)


print(
    "Exact duplicate rows removed:",
    before - len(df),
)


# ============================================================
# REMOVE CONFLICTING URL LABELS
# ============================================================

label_counts = (
    df.groupby("URL")["label"]
    .nunique()
)


conflicting_urls = (
    label_counts[
        label_counts > 1
    ]
    .index
)


if len(conflicting_urls) > 0:

    print(
        "Conflicting URLs removed:",
        len(conflicting_urls),
    )

    df = df[
        ~df["URL"].isin(
            conflicting_urls
        )
    ].copy()

else:

    print(
        "Conflicting URLs removed: 0"
    )


df = df.reset_index(
    drop=True
)


print(
    "Final training rows:",
    len(df),
)


# ============================================================
# CHECK CLASS DISTRIBUTION
# ============================================================

print()
print("Final class distribution:")
print()

class_counts = (
    df["label"]
    .value_counts()
    .sort_index()
)

print(class_counts)

if len(class_counts) < 2:

    print()
    print(
        "ERROR: Training data must contain "
        "both classes: 0 and 1."
    )

    sys.exit(1)


# ============================================================
# AUGMENT LEGITIMATE URLs (www / apex debiasing)
# ============================================================

print()
print(
    "Augmenting legitimate URLs with www/apex variants..."
)
print()

before_aug = len(df)

df = augment_legitimate_urls(df)

print(
    "Rows before augmentation:",
    f"{before_aug:,}",
)

print(
    "Rows after augmentation:",
    f"{len(df):,}",
)

print(
    "Augmented rows added:",
    f"{len(df) - before_aug:,}",
)


print()
print("Class distribution after augmentation:")
print()

print(
    df["label"].value_counts().sort_index()
)


# ============================================================
# STEP 5 - EXTRACT URL FEATURES
# ============================================================

print()
print(
    "[5/10] Extracting URL-only features..."
)
print()


print(
    "Number of features:",
    len(FEATURE_NAMES),
)


if len(FEATURE_NAMES) != 48:

    print(
        "ERROR: Expected exactly 48 features."
    )

    sys.exit(1)


print()
print("Feature order:")
print()


for index, name in enumerate(
    FEATURE_NAMES,
    start=1,
):

    print(
        f"{index:02d}. {name}"
    )


# ============================================================
# FEATURE EXTRACTION
# ============================================================

feature_rows = []

total = len(df)


for index, url in enumerate(
    df["URL"],
    start=1,
):

    try:

        features = extract_url_features(
            url
        )

        feature_rows.append(
            [
                features[name]
                for name in FEATURE_NAMES
            ]
        )

    except Exception as exc:

        print()
        print(
            "ERROR extracting URL:"
        )

        print(url)

        print()
        print(
            "Exception:"
        )

        print(
            repr(exc)
        )

        sys.exit(1)


    if (
        index % 25000 == 0
        or index == total
    ):

        percentage = (
            index / total
        ) * 100

        print(
            f"Processed "
            f"{index:,}/{total:,}"
            f" ({percentage:.1f}%)"
        )


# ============================================================
# CREATE FEATURE MATRIX
# ============================================================

X = pd.DataFrame(
    feature_rows,
    columns=FEATURE_NAMES,
)


y = df[
    "label"
].copy()


print()
print(
    "Feature matrix:",
    X.shape,
)


print(
    "Target vector:",
    y.shape,
)


# ============================================================
# STEP 6 - CLEAN FEATURES
# ============================================================

print()
print(
    "[6/10] Cleaning feature matrix..."
)
print()


X = X.replace(
    [np.inf, -np.inf],
    np.nan,
)


X = X.fillna(
    0.0
)


X = X.astype(
    np.float32
)


print(
    "Missing values:",
    int(
        X.isna()
        .sum()
        .sum()
    ),
)


# ============================================================
# FINAL FEATURE COUNT CHECK
# ============================================================

if X.shape[1] != 48:

    print()
    print(
        "ERROR: Feature matrix does not "
        "contain exactly 48 features."
    )

    sys.exit(1)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

print()
print(
    "Splitting dataset..."
)
print()


(
    X_train,
    X_test,
    y_train,
    y_test,
) = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=y,
)


print(
    "Training samples:",
    len(X_train),
)


print(
    "Testing samples:",
    len(X_test),
)


# ============================================================
# STEP 7 - TRAIN MODEL
# ============================================================

print()
print(
    "[7/10] Training XGBoost model..."
)
print()


print(
    "Model parameters:"
)


for key, value in MODEL_PARAMS.items():

    print(
        f"  {key}: {value}"
    )


print()


model = XGBClassifier(
    **MODEL_PARAMS
)


model.fit(
    X_train,
    y_train,
)


print()
print(
    "Training completed."
)


# ============================================================
# STEP 8 - EVALUATE MODEL
# ============================================================

print()
print(
    "[8/10] Evaluating model..."
)
print()


predictions = model.predict(
    X_test
)


probabilities = (
    model.predict_proba(
        X_test
    )[:, 1]
)


accuracy = accuracy_score(
    y_test,
    predictions,
)


roc_auc = roc_auc_score(
    y_test,
    probabilities,
)


cm = confusion_matrix(
    y_test,
    predictions,
)


report = classification_report(
    y_test,
    predictions,
    target_names=[
        "Phishing",
        "Legitimate",
    ],
)


print("=" * 70)
print("MODEL RESULTS")
print("=" * 70)
print()


print(
    "Test Accuracy:",
    round(
        accuracy * 100,
        4,
    ),
    "%",
)


print(
    "ROC-AUC:",
    round(
        roc_auc,
        4,
    ),
)


print()
print(
    "Confusion Matrix:"
)
print(cm)


print()
print(
    "Classification Report:"
)
print(report)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

print()
print(
    "TOP FEATURE IMPORTANCES"
)
print()


importance = pd.Series(
    model.feature_importances_,
    index=FEATURE_NAMES,
)


importance = importance.sort_values(
    ascending=False
)


print(
    importance
    .head(20)
    .to_string()
)


# ============================================================
# STEP 9 - REAL-WORLD SANITY CHECK
# ============================================================

print()
print(
    "[9/10] Running real-world sanity checks..."
)
print()


# ============================================================
# LEGITIMATE URL CHECK
# ============================================================

print("=" * 70)
print(
    "LEGITIMATE WEBSITE CHECK"
)
print("=" * 70)
print()


legitimate_results = _evaluate_urls(
    model,
    LEGITIMATE_TEST_URLS,
    expected_label=1,
)


print()


print(
    "Legitimate sanity checks passed:",
    f"{sum(legitimate_results)}/"
    f"{len(LEGITIMATE_TEST_URLS)}",
)


# ============================================================
# LEGITIMATE APEX URL CHECK (hard gate)
# ============================================================

print()
print("=" * 70)
print(
    "LEGITIMATE APEX URL CHECK"
)
print("=" * 70)
print()


apex_results = _evaluate_urls(
    model,
    LEGITIMATE_APEX_TEST_URLS,
    expected_label=1,
)


print()


print(
    "Apex URL checks passed:",
    f"{sum(apex_results)}/"
    f"{len(LEGITIMATE_APEX_TEST_URLS)}",
)


# ============================================================
# PHISHING URL CHECK
# ============================================================

print()
print("=" * 70)
print(
    "PHISHING WEBSITE CHECK"
)
print("=" * 70)
print()


phishing_results = _evaluate_urls(
    model,
    PHISHING_TEST_URLS,
    expected_label=0,
)


print()


print(
    "Phishing sanity checks passed:",
    f"{sum(phishing_results)}/"
    f"{len(PHISHING_TEST_URLS)}",
)


# ============================================================
# VALIDATION GATE (must pass before save)
# ============================================================

legitimate_gate_passed = all(legitimate_results)
apex_gate_passed = all(apex_results)
phishing_gate_passed = all(phishing_results)

validation_passed = (
    legitimate_gate_passed
    and apex_gate_passed
    and phishing_gate_passed
)


print()
print("=" * 70)
print(
    "VALIDATION GATE"
)
print("=" * 70)
print()


print(
    "Legitimate URL gate:",
    "PASS" if legitimate_gate_passed else "FAIL",
)

print(
    "Legitimate apex URL gate:",
    "PASS" if apex_gate_passed else "FAIL",
)

print(
    "Phishing URL gate:",
    "PASS" if phishing_gate_passed else "FAIL",
)


if not validation_passed:

    print()
    print(
        "ERROR: Model failed validation gate. "
        "Model will NOT be saved."
    )

    print()
    print("=" * 70)
    print(
        "TRAINING FINISHED (MODEL NOT SAVED)"
    )
    print("=" * 70)
    print()

    sys.exit(1)


# ============================================================
# STEP 10 - SAVE MODEL
# ============================================================

print()
print(
    "[10/10] Saving model..."
)
print()


MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


joblib.dump(
    model,
    MODEL_PATH,
)


print()
print("=" * 70)
print(
    "MODEL SAVED SUCCESSFULLY"
)
print("=" * 70)
print()


print(
    "Model:",
    MODEL_PATH,
)


print(
    "Number of model features:",
    len(
        model.feature_names_in_
    ),
)


print()
print(
    "Model feature order:"
)


print(
    list(
        model.feature_names_in_
    )
)


print()
print("=" * 70)
print(
    "TRAINING FINISHED"
)
print("=" * 70)
print()