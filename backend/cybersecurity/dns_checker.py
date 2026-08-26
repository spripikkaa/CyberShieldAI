import logging
import socket
from typing import Any

import dns.exception
import dns.resolver

from backend.cybersecurity.exceptions import (
    DnsDomainNotFoundError,
    DnsLookupError,
    InvalidDomainError,
)
from backend.cybersecurity.whois_checker import extract_domain

logger = logging.getLogger(__name__)

QUERY_TIMEOUT_SECONDS = 10


def _get_resolver() -> dns.resolver.Resolver:
    """Create a DNS resolver with a bounded query timeout."""
    resolver = dns.resolver.Resolver()
    resolver.lifetime = QUERY_TIMEOUT_SECONDS
    return resolver


def _format_rdata(record: Any, rdtype: str) -> str:
    """Format a DNS resource record into a readable string."""
    if rdtype == "MX":
        return f"{record.preference} {str(record.exchange).rstrip('.')}"
    if rdtype == "TXT":
        parts = record.strings
        decoded = [
            part.decode("utf-8") if isinstance(part, bytes) else str(part) for part in parts
        ]
        return "".join(decoded)
    return str(record).rstrip(".")


def _query_records(domain: str, rdtype: str) -> list[str]:
    """Query a single DNS record type and return formatted results."""
    resolver = _get_resolver()
    try:
        answers = resolver.resolve(domain, rdtype)
    except dns.resolver.NXDOMAIN as exc:
        raise DnsDomainNotFoundError(f"Domain '{domain}' does not exist (NXDOMAIN).") from exc
    except dns.resolver.NoAnswer:
        return []
    except dns.resolver.NoNameservers as exc:
        raise DnsLookupError(f"No nameservers responded for '{domain}'.") from exc
    except (dns.resolver.LifetimeTimeout, dns.exception.Timeout) as exc:
        raise DnsLookupError(f"DNS query timed out for '{domain}'.") from exc
    except dns.resolver.NoResolverConfiguration as exc:
        raise DnsLookupError("DNS resolver is not configured on this system.") from exc
    except Exception as exc:
        logger.exception("Unexpected DNS error for domain='%s' rdtype='%s'", domain, rdtype)
        raise DnsLookupError(f"DNS lookup failed for '{domain}'.") from exc

    return [_format_rdata(record, rdtype) for record in answers]


def _resolve_ip_address(domain: str, a_records: list[str]) -> str | None:
    """Return the primary IP address from A records or a socket fallback."""
    if a_records:
        return a_records[0]

    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None


def lookup_dns(url: str) -> dict[str, Any]:
    """
    Perform DNS analysis for the domain extracted from a website URL.

    Queries A, AAAA, MX, NS, CNAME, and TXT records using dnspython.
    """
    domain = extract_domain(url)

    a_records = _query_records(domain, "A")
    aaaa_records = _query_records(domain, "AAAA")
    mx_records = _query_records(domain, "MX")
    ns_records = _query_records(domain, "NS")
    cname_records = _query_records(domain, "CNAME")
    txt_records = _query_records(domain, "TXT")

    if not any([a_records, aaaa_records, mx_records, ns_records, cname_records, txt_records]):
        # Re-raise if the domain truly does not exist; otherwise return empty record sets.
        try:
            _query_records(domain, "SOA")
        except DnsDomainNotFoundError:
            raise

    return {
        "domain_name": domain,
        "ip_address": _resolve_ip_address(domain, a_records),
        "a_records": a_records,
        "aaaa_records": aaaa_records,
        "mx_records": mx_records,
        "ns_records": ns_records,
        "cname": cname_records,
        "txt_records": txt_records,
    }
