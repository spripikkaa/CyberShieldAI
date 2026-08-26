"""
CyberShield AI
Feature Extractor Compatibility Layer

IMPORTANT:
The actual URL feature extraction is implemented only in:

    backend.ml.url_feature_extractor

This file exists so older backend code that imports
feature_extractor.py does not break.
"""

from backend.ml.features import (
    FEATURE_NAMES,
)

from backend.ml.url_feature_extractor import (
    COMMON_TLDS,
    SUSPICIOUS_WORDS,
    extract_features_from_url,
    extract_url_features,
)


__all__ = [
    "FEATURE_NAMES",
    "COMMON_TLDS",
    "SUSPICIOUS_WORDS",
    "extract_url_features",
    "extract_features_from_url",
]