"""
CyberShield AI
Feature Definitions

This file contains the exact feature order used by the
URL-only XGBoost phishing detection model.

Labels:
    0 = Phishing
    1 = Legitimate
"""
FEATURE_NAMES: list[str] = [
    "url_length",
    "domain_length",
    "path_length",
    "query_length",
    "fragment_length",
    "num_dots",
    "num_hyphens",
    "num_underscores",
    "num_slashes",
    "num_digits",
    "num_letters",
    "num_special_chars",
    "digit_ratio",
    "letter_ratio",
    "special_char_ratio",
    "num_subdomains",
    "has_ip",
    "has_https",
    "has_http",
    "has_www",
    "has_at_symbol",
    "has_question_mark",
    "has_equal",
    "has_ampersand",
    "has_percent",
    "has_hash",
    "has_double_slash",
    "has_port",
    "has_punycode",
    "num_query_parameters",
    "num_suspicious_words",
    "has_suspicious_word",
    "domain_entropy",
    "path_entropy",
    "domain_has_digit",
    "domain_digit_ratio",
    "path_has_digit",
    "path_digit_ratio",
    "tld_length",
    "tld_is_common",
    "domain_hyphen_ratio",
    "path_special_ratio",
    "url_has_encoded_char",
    "num_encoded_chars",
    "url_has_long_numeric_sequence",
    "max_numeric_sequence",
    "domain_repeated_char_ratio",
    "path_repeated_char_ratio",
]
# ============================================================
# LABEL DEFINITIONS
# ============================================================
LABEL_TO_CLASS: dict[int, str] = {
    0: "Phishing",
    1: "Legitimate",
}
# ============================================================
# SAFETY CHECK
# ============================================================
if len(FEATURE_NAMES) != 48:
    raise RuntimeError(
        f"Expected exactly 48 features, "
        f"but found {len(FEATURE_NAMES)}."
    )
