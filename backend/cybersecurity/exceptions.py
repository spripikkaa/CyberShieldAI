"""Custom exceptions for cybersecurity analysis modules."""


class InvalidDomainError(Exception):
    """Raised when a URL or domain string cannot be parsed."""


class WhoisDomainNotFoundError(Exception):
    """Raised when WHOIS lookup returns no registration data for the domain."""


class WhoisLookupError(Exception):
    """Raised when the WHOIS query fails due to network or server errors."""


class SslConnectionError(Exception):
    """Raised when an SSL/TLS connection cannot be established."""


class SslCertificateError(Exception):
    """Raised when a certificate is present but cannot be parsed."""


class DnsDomainNotFoundError(Exception):
    """Raised when DNS lookup returns NXDOMAIN for the domain."""


class DnsLookupError(Exception):
    """Raised when a DNS query fails due to resolver or network errors."""
