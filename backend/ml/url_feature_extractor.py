"""
CyberShield AI
URL-Only Feature Extractor

IMPORTANT:
This extractor uses ONLY the URL string.

It does NOT:
- visit the website
- make HTTP requests
- access robots.txt
- download HTML
- inspect JavaScript
- inspect page source

Therefore the exact same feature extraction can be used
during training and during real-time prediction.
"""

import math
import re
from collections import Counter
from urllib.parse import parse_qs, urlparse


# ============================================================
# SUSPICIOUS WORDS
# ============================================================

SUSPICIOUS_WORDS = {
    "login",
    "signin",
    "sign-in",
    "verify",
    "verification",
    "account",
    "update",
    "secure",
    "security",
    "confirm",
    "confirmation",
    "password",
    "credential",
    "authenticate",
    "authentication",
    "wallet",
    "payment",
    "pay",
    "bank",
    "banking",
    "invoice",
    "billing",
    "bonus",
    "free",
    "gift",
    "reward",
    "claim",
    "unlock",
    "suspended",
    "suspend",
    "urgent",
    "alert",
    "recover",
    "recovery",
    "limited",
    "webscr",
}


# ============================================================
# COMMON LEGITIMATE TLDs
# ============================================================

COMMON_TLDS = {
    "com",
    "org",
    "net",
    "edu",
    "gov",
    "mil",
    "int",
    "in",
    "co",
    "uk",
    "us",
    "ca",
    "au",
    "de",
    "fr",
    "jp",
    "cn",
    "io",
    "ai",
    "app",
    "dev",
    "tech",
    "me",
    "info",
    "biz",
}


# ============================================================
# URL FEATURE ORDER
# ============================================================

FEATURE_NAMES = [
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
# HELPER FUNCTIONS
# ============================================================

def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0

    return float(numerator) / float(denominator)


def _entropy(value: str) -> float:
    """
    Shannon entropy of a string.
    """

    if not value:
        return 0.0

    counts = Counter(value)
    length = len(value)

    entropy = 0.0

    for count in counts.values():
        probability = count / length

        entropy -= probability * math.log2(probability)

    return float(entropy)


def _count_letters(value: str) -> int:
    return sum(char.isalpha() for char in value)


def _count_digits(value: str) -> int:
    return sum(char.isdigit() for char in value)


def _count_special_chars(value: str) -> int:
    return sum(
        not char.isalnum()
        for char in value
    )


def _max_numeric_sequence(value: str) -> int:
    matches = re.findall(r"\d+", value)

    if not matches:
        return 0

    return max(len(item) for item in matches)


def _count_encoded_chars(value: str) -> int:
    """
    Counts percent-encoded sequences such as:
    %20
    %3D
    %2F
    """

    return len(
        re.findall(
            r"%[0-9a-fA-F]{2}",
            value,
        )
    )


def _repeated_char_ratio(value: str) -> float:
    """
    Measures repeated adjacent characters.

    Example:
    aaabbbcc -> relatively high ratio
    google   -> some repetition
    """

    if len(value) < 2:
        return 0.0

    repeated = 0

    for i in range(1, len(value)):
        if value[i] == value[i - 1]:
            repeated += 1

    return _safe_ratio(
        repeated,
        len(value) - 1,
    )


def _normalize_url(url: str) -> str:
    """
    Make sure urlparse correctly identifies the hostname.
    """

    url = str(url).strip()

    if not url:
        return ""

    if "://" not in url:
        url = "http://" + url

    return url


def _is_ip_address(hostname: str) -> bool:
    """
    Detect IPv4-style hostnames.
    """

    if not hostname:
        return False

    ipv4_pattern = (
        r"^(?:\d{1,3}\.){3}\d{1,3}$"
    )

    if not re.match(ipv4_pattern, hostname):
        return False

    parts = hostname.split(".")

    try:
        return all(
            0 <= int(part) <= 255
            for part in parts
        )
    except ValueError:
        return False


def _extract_tld(hostname: str) -> str:
    if not hostname:
        return ""

    hostname = hostname.lower().strip(".")

    parts = hostname.split(".")

    if len(parts) < 2:
        return ""

    return parts[-1]


def _count_suspicious_words(url: str) -> int:
    url_lower = url.lower()

    count = 0

    for word in SUSPICIOUS_WORDS:
        if word in url_lower:
            count += 1

    return count


# ============================================================
# MAIN FEATURE EXTRACTION
# ============================================================

def extract_url_features(url: str) -> dict[str, float]:
    """
    Extract deterministic URL-only features.

    Returns:
        Dictionary containing FEATURE_NAMES.
    """

    original_url = str(url).strip()

    normalized_url = _normalize_url(original_url)

    parsed = urlparse(normalized_url)

    hostname = (
        parsed.hostname.lower()
        if parsed.hostname
        else ""
    )

    path = parsed.path or ""
    query = parsed.query or ""
    fragment = parsed.fragment or ""

    domain = hostname

    tld = _extract_tld(hostname)

    # --------------------------------------------------------
    # Basic URL statistics
    # --------------------------------------------------------

    url_length = len(original_url)

    domain_length = len(domain)

    path_length = len(path)

    query_length = len(query)

    fragment_length = len(fragment)

    num_dots = original_url.count(".")

    num_hyphens = original_url.count("-")

    num_underscores = original_url.count("_")

    num_slashes = original_url.count("/")

    num_digits = _count_digits(original_url)

    num_letters = _count_letters(original_url)

    num_special_chars = _count_special_chars(original_url)

    # --------------------------------------------------------
    # Ratios
    # --------------------------------------------------------

    digit_ratio = _safe_ratio(
        num_digits,
        url_length,
    )

    letter_ratio = _safe_ratio(
        num_letters,
        url_length,
    )

    special_char_ratio = _safe_ratio(
        num_special_chars,
        url_length,
    )

    # --------------------------------------------------------
    # Subdomains
    # --------------------------------------------------------

    domain_parts = [
        part
        for part in domain.split(".")
        if part
    ]

    num_subdomains = max(
        len(domain_parts) - 2,
        0,
    )

    # --------------------------------------------------------
    # Protocol
    # --------------------------------------------------------

    has_https = int(
        parsed.scheme.lower() == "https"
    )

    has_http = int(
        parsed.scheme.lower() == "http"
    )

    # --------------------------------------------------------
    # Common URL structures
    # --------------------------------------------------------

    has_ip = int(
        _is_ip_address(hostname)
    )

    has_www = int(
        hostname.startswith("www.")
    )

    has_at_symbol = int(
        "@" in original_url
    )

    has_question_mark = int(
        "?" in original_url
    )

    has_equal = int(
        "=" in original_url
    )

    has_ampersand = int(
        "&" in original_url
    )

    has_percent = int(
        "%" in original_url
    )

    has_hash = int(
        "#" in original_url
    )

    # Detect // after the scheme.
    after_scheme = original_url

    if "://" in after_scheme:
        after_scheme = after_scheme.split(
            "://",
            1,
        )[1]

    has_double_slash = int(
        "//" in after_scheme
    )

    # --------------------------------------------------------
    # Port
    # --------------------------------------------------------

    has_port = int(
        parsed.port is not None
        if parsed.hostname
        else False
    )

    # --------------------------------------------------------
    # Punycode
    # --------------------------------------------------------

    has_punycode = int(
        "xn--" in hostname.lower()
    )

    # --------------------------------------------------------
    # Query parameters
    # --------------------------------------------------------

    try:
        query_parameters = len(
            parse_qs(
                query,
                keep_blank_values=True,
            )
        )
    except Exception:
        query_parameters = 0

    # --------------------------------------------------------
    # Suspicious words
    # --------------------------------------------------------

    num_suspicious_words = (
        _count_suspicious_words(
            original_url
        )
    )

    has_suspicious_word = int(
        num_suspicious_words > 0
    )

    # --------------------------------------------------------
    # Entropy
    # --------------------------------------------------------

    domain_entropy = _entropy(domain)

    path_entropy = _entropy(path)

    # --------------------------------------------------------
    # Domain digits
    # --------------------------------------------------------

    domain_digits = _count_digits(domain)

    domain_has_digit = int(
        domain_digits > 0
    )

    domain_digit_ratio = _safe_ratio(
        domain_digits,
        len(domain),
    )

    # --------------------------------------------------------
    # Path digits
    # --------------------------------------------------------

    path_digits = _count_digits(path)

    path_has_digit = int(
        path_digits > 0
    )

    path_digit_ratio = _safe_ratio(
        path_digits,
        len(path),
    )

    # --------------------------------------------------------
    # TLD
    # --------------------------------------------------------

    tld_length = len(tld)

    tld_is_common = int(
        tld in COMMON_TLDS
    )

    # --------------------------------------------------------
    # Domain hyphen ratio
    # --------------------------------------------------------

    domain_hyphens = domain.count("-")

    domain_hyphen_ratio = _safe_ratio(
        domain_hyphens,
        len(domain),
    )

    # --------------------------------------------------------
    # Path special-character ratio
    # --------------------------------------------------------

    path_special_chars = _count_special_chars(
        path
    )

    path_special_ratio = _safe_ratio(
        path_special_chars,
        len(path),
    )

    # --------------------------------------------------------
    # Encoded characters
    # --------------------------------------------------------

    num_encoded_chars = _count_encoded_chars(
        original_url
    )

    url_has_encoded_char = int(
        num_encoded_chars > 0
    )

    # --------------------------------------------------------
    # Numeric sequences
    # --------------------------------------------------------

    max_numeric_sequence = _max_numeric_sequence(
        original_url
    )

    url_has_long_numeric_sequence = int(
        max_numeric_sequence >= 4
    )

    # --------------------------------------------------------
    # Repeated characters
    # --------------------------------------------------------

    domain_repeated_char_ratio = (
        _repeated_char_ratio(domain)
    )

    path_repeated_char_ratio = (
        _repeated_char_ratio(path)
    )

    # ========================================================
    # FINAL FEATURE DICTIONARY
    # ========================================================

    features = {
        "url_length": float(url_length),
        "domain_length": float(domain_length),
        "path_length": float(path_length),
        "query_length": float(query_length),
        "fragment_length": float(fragment_length),

        "num_dots": float(num_dots),
        "num_hyphens": float(num_hyphens),
        "num_underscores": float(num_underscores),
        "num_slashes": float(num_slashes),
        "num_digits": float(num_digits),
        "num_letters": float(num_letters),
        "num_special_chars": float(num_special_chars),

        "digit_ratio": float(digit_ratio),
        "letter_ratio": float(letter_ratio),
        "special_char_ratio": float(special_char_ratio),

        "num_subdomains": float(num_subdomains),

        "has_ip": float(has_ip),
        "has_https": float(has_https),
        "has_http": float(has_http),
        "has_www": float(has_www),

        "has_at_symbol": float(has_at_symbol),
        "has_question_mark": float(has_question_mark),
        "has_equal": float(has_equal),
        "has_ampersand": float(has_ampersand),
        "has_percent": float(has_percent),
        "has_hash": float(has_hash),
        "has_double_slash": float(has_double_slash),

        "has_port": float(has_port),
        "has_punycode": float(has_punycode),

        "num_query_parameters": float(
            query_parameters
        ),

        "num_suspicious_words": float(
            num_suspicious_words
        ),

        "has_suspicious_word": float(
            has_suspicious_word
        ),

        "domain_entropy": float(
            domain_entropy
        ),

        "path_entropy": float(
            path_entropy
        ),

        "domain_has_digit": float(
            domain_has_digit
        ),

        "domain_digit_ratio": float(
            domain_digit_ratio
        ),

        "path_has_digit": float(
            path_has_digit
        ),

        "path_digit_ratio": float(
            path_digit_ratio
        ),

        "tld_length": float(
            tld_length
        ),

        "tld_is_common": float(
            tld_is_common
        ),

        "domain_hyphen_ratio": float(
            domain_hyphen_ratio
        ),

        "path_special_ratio": float(
            path_special_ratio
        ),

        "url_has_encoded_char": float(
            url_has_encoded_char
        ),

        "num_encoded_chars": float(
            num_encoded_chars
        ),

        "url_has_long_numeric_sequence": float(
            url_has_long_numeric_sequence
        ),

        "max_numeric_sequence": float(
            max_numeric_sequence
        ),

        "domain_repeated_char_ratio": float(
            domain_repeated_char_ratio
        ),

        "path_repeated_char_ratio": float(
            path_repeated_char_ratio
        ),
    }

    # --------------------------------------------------------
    # Guarantee exact feature order
    # --------------------------------------------------------

    return {
        name: features[name]
        for name in FEATURE_NAMES
    }


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

def extract_features_from_url(url: str) -> dict[str, float]:
    """
    Compatibility wrapper.

    Your existing backend already uses this function name,
    so we keep the same public function.
    """

    return extract_url_features(url)