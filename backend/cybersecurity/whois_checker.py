import logging
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import whois
from whois.exceptions import WhoisDomainNotFoundError as PyWhoisDomainNotFoundError

from backend.cybersecurity.exceptions import (
    InvalidDomainError,
    WhoisDomainNotFoundError,
    WhoisLookupError,
)

logger = logging.getLogger(__name__)


def extract_domain(url: str) -> str:
    """
    Extract a registrable domain from a full website URL or bare domain string.

    Examples:
        https://www.example.com/path -> example.com
        example.com -> example.com
    """
    cleaned = url.strip()
    if not cleaned:
        raise InvalidDomainError("Website URL is required.")

    # Allow bare domains by assuming HTTPS when no scheme is present.
    if "://" not in cleaned:
        cleaned = f"https://{cleaned}"

    parsed = urlparse(cleaned)
    host = parsed.netloc or parsed.path.split("/")[0]

    if host.startswith("www."):
        host = host[4:]

    if not host or "." not in host:
        raise InvalidDomainError(f"Could not extract a valid domain from '{url}'.")

    return host.lower()


def _first_value(value: Any) -> Any:
    """WHOIS fields may be returned as a single value or a list."""
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _normalize_datetime(value: Any) -> datetime | None:
    """Convert WHOIS date values into a timezone-aware datetime."""
    value = _first_value(value)
    if value is None:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed

    return None


def _format_datetime(value: datetime | None) -> str | None:
    """Serialize datetimes as ISO-8601 strings for API responses."""
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat()


def _normalize_text(value: Any) -> str | None:
    """Convert WHOIS text fields to a clean string."""
    value = _first_value(value)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def compute_domain_age(creation_date: datetime | None) -> str | None:
    """Calculate human-readable domain age from the creation date."""
    if creation_date is None:
        return None

    now = datetime.now(timezone.utc)
    if creation_date.tzinfo is None:
        creation_date = creation_date.replace(tzinfo=timezone.utc)

    total_days = (now - creation_date).days
    if total_days < 0:
        return None

    years, remaining_days = divmod(total_days, 365)
    if years > 0:
        year_label = "year" if years == 1 else "years"
        day_label = "day" if remaining_days == 1 else "days"
        return f"{years} {year_label}, {remaining_days} {day_label}"

    day_label = "day" if total_days == 1 else "days"
    return f"{total_days} {day_label}"


def lookup_whois(url: str) -> dict[str, str | None]:
    """
    Perform a WHOIS lookup for the domain extracted from the given website URL.

    Returns a dictionary with domain registration details.
    """
    domain = extract_domain(url)

    try:
        record = whois.whois(domain)
    except PyWhoisDomainNotFoundError as exc:
        raise WhoisDomainNotFoundError(f"No WHOIS registration found for '{domain}'.") from exc
    except Exception as exc:
        logger.exception("WHOIS lookup failed for domain '%s'", domain)
        raise WhoisLookupError(f"WHOIS lookup failed for '{domain}'.") from exc

    domain_name = _normalize_text(record.domain_name) or domain
    registrar = _normalize_text(record.registrar)
    creation_dt = _normalize_datetime(record.creation_date)
    expiration_dt = _normalize_datetime(record.expiration_date)
    country = _normalize_text(record.country)

    if not any([registrar, creation_dt, expiration_dt, country]):
        raise WhoisDomainNotFoundError(f"No WHOIS registration found for '{domain}'.")

    return {
        "domain_name": domain_name,
        "registrar": registrar,
        "creation_date": _format_datetime(creation_dt),
        "expiration_date": _format_datetime(expiration_dt),
        "domain_age": compute_domain_age(creation_dt),
        "country": country,
    }
