import logging
import socket
import ssl
from datetime import datetime, timezone
from typing import Any, Literal
from urllib.parse import urlparse

from backend.cybersecurity.exceptions import (
    InvalidDomainError,
    SslCertificateError,
    SslConnectionError,
)

logger = logging.getLogger(__name__)

DEFAULT_SSL_PORT = 443
CONNECTION_TIMEOUT_SECONDS = 10

# Common X.509 signature algorithm OIDs found in DER-encoded certificates.
_SIGNATURE_OID_MAP: dict[bytes, str] = {
    b"\x2a\x86\x48\x86\xf7\x0d\x01\x01\x0b": "sha256WithRSAEncryption",
    b"\x2a\x86\x48\x86\xf7\x0d\x01\x01\x0c": "sha512WithRSAEncryption",
    b"\x2a\x86\x48\x86\xf7\x0d\x01\x01\x0d": "sha384WithRSAEncryption",
    b"\x2a\x86\x48\x86\xf7\x0d\x01\x01\x01": "sha1WithRSAEncryption",
    b"\x2a\x86\x48\xce\x3d\x04\x03\x02": "ecdsa-with-SHA256",
    b"\x2a\x86\x48\xce\x3d\x04\x03\x03": "ecdsa-with-SHA384",
    b"\x2a\x86\x48\xce\x3d\x04\x03\x04": "ecdsa-with-SHA512",
}


def extract_host_and_port(url: str) -> tuple[str, int]:
    """
    Extract hostname and port from a website URL for SSL inspection.

    Preserves subdomains (e.g. www) because they matter for SNI during TLS.
    """
    cleaned = url.strip()
    if not cleaned:
        raise InvalidDomainError("Website URL is required.")

    if "://" not in cleaned:
        cleaned = f"https://{cleaned}"

    parsed = urlparse(cleaned)
    host = parsed.hostname or parsed.netloc.split(":")[0]

    if not host or "." not in host:
        raise InvalidDomainError(f"Could not extract a valid host from '{url}'.")

    port = parsed.port or DEFAULT_SSL_PORT
    return host.lower(), port


def _format_distinguished_name(name_tuple: tuple[Any, ...]) -> str:
    """Convert a getpeercert() subject/issuer tuple into a readable string."""
    parts: list[str] = []
    for rdn in name_tuple:
        for attribute_type, attribute_value in rdn:
            parts.append(f"{attribute_type}={attribute_value}")
    return ", ".join(parts)


def _parse_cert_datetime(value: str) -> datetime:
    """Parse OpenSSL-style certificate timestamps."""
    return datetime.strptime(value, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)


def _format_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _extract_signature_algorithm(der_certificate: bytes) -> str | None:
    """
    Best-effort signature algorithm detection from DER certificate bytes.

    stdlib getpeercert() does not expose this field, so known OIDs are matched
    directly in the encoded certificate when available.
    """
    for oid_bytes, algorithm_name in _SIGNATURE_OID_MAP.items():
        if oid_bytes in der_certificate:
            return algorithm_name
    return None


def _build_result_from_certificate(
    *,
    cert: dict[str, Any],
    der_certificate: bytes,
    ssl_status: Literal["Valid", "Invalid"],
    https_status: Literal["Enabled", "Disabled"],
) -> dict[str, Any]:
    """Normalize parsed certificate data into API response fields."""
    not_before_raw = cert.get("notBefore")
    not_after_raw = cert.get("notAfter")

    valid_from = None
    expiry_date = None
    days_remaining = None

    if not_before_raw:
        valid_from_dt = _parse_cert_datetime(not_before_raw)
        valid_from = _format_datetime(valid_from_dt)

    if not_after_raw:
        expiry_dt = _parse_cert_datetime(not_after_raw)
        expiry_date = _format_datetime(expiry_dt)
        days_remaining = (expiry_dt - datetime.now(timezone.utc)).days

        # Flag expired certificates even when fetched without strict verification.
        if days_remaining < 0:
            ssl_status = "Invalid"

    return {
        "ssl_status": ssl_status,
        "https_status": https_status,
        "certificate_issuer": _format_distinguished_name(cert["issuer"])
        if cert.get("issuer")
        else None,
        "subject": _format_distinguished_name(cert["subject"]) if cert.get("subject") else None,
        "valid_from": valid_from,
        "expiry_date": expiry_date,
        "days_remaining": days_remaining,
        "signature_algorithm": _extract_signature_algorithm(der_certificate),
    }


def _fetch_certificate(host: str, port: int) -> tuple[dict[str, Any], bytes, bool]:
    """
    Connect with TLS and return certificate data plus verification outcome.

    Returns:
        certificate dict, DER bytes, and whether verification succeeded.
    """
    verified_context = ssl.create_default_context()

    try:
        with socket.create_connection((host, port), timeout=CONNECTION_TIMEOUT_SECONDS) as raw_socket:
            with verified_context.wrap_socket(
                raw_socket,
                server_hostname=host,
            ) as tls_socket:
                cert = tls_socket.getpeercert()
                der_certificate = tls_socket.getpeercert(binary_form=True)
                if not cert or not der_certificate:
                    raise SslCertificateError(f"Host '{host}' did not provide a certificate.")
                return cert, der_certificate, True
    except ssl.SSLError:
        logger.warning(
            "Certificate verification failed for host='%s'; retrying without verification.",
            host,
        )
    except (socket.timeout, TimeoutError, OSError) as exc:
        raise SslConnectionError(
            f"Could not establish an SSL connection to '{host}' on port {port}."
        ) from exc

    # Retry without verification to still return certificate metadata for invalid certs.
    unverified_context = ssl.create_default_context()
    unverified_context.check_hostname = False
    unverified_context.verify_mode = ssl.CERT_NONE

    try:
        with socket.create_connection((host, port), timeout=CONNECTION_TIMEOUT_SECONDS) as raw_socket:
            with unverified_context.wrap_socket(raw_socket, server_hostname=host) as tls_socket:
                cert = tls_socket.getpeercert()
                der_certificate = tls_socket.getpeercert(binary_form=True)
                if not cert or not der_certificate:
                    raise SslCertificateError(f"Host '{host}' did not provide a certificate.")
                return cert, der_certificate, False
    except (socket.timeout, TimeoutError) as exc:
        raise SslConnectionError(
            f"Timed out while connecting to '{host}' on port {port}."
        ) from exc
    except OSError as exc:
        raise SslConnectionError(
            f"Could not establish an SSL connection to '{host}' on port {port}."
        ) from exc
    except ssl.SSLError as exc:
        raise SslConnectionError(
            f"SSL handshake failed for '{host}' on port {port}."
        ) from exc


def check_ssl_certificate(url: str) -> dict[str, Any]:
    """
    Analyze the SSL/TLS certificate for the host extracted from a website URL.
    """
    host, port = extract_host_and_port(url)

    try:
        cert, der_certificate, verified = _fetch_certificate(host, port)
    except SslConnectionError:
        return {
            "ssl_status": "Invalid",
            "https_status": "Disabled",
            "certificate_issuer": None,
            "subject": None,
            "valid_from": None,
            "expiry_date": None,
            "days_remaining": None,
            "signature_algorithm": None,
        }
    except SslCertificateError:
        raise

    ssl_status: Literal["Valid", "Invalid"] = "Valid" if verified else "Invalid"
    return _build_result_from_certificate(
        cert=cert,
        der_certificate=der_certificate,
        ssl_status=ssl_status,
        https_status="Enabled",
    )
