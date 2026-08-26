import logging

from fastapi import APIRouter, HTTPException, Query, status

from backend.api.schemas.dns import DnsResponse
from backend.cybersecurity.dns_checker import lookup_dns
from backend.cybersecurity.exceptions import (
    DnsDomainNotFoundError,
    DnsLookupError,
    InvalidDomainError,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["dns"])


@router.get(
    "/dns",
    response_model=DnsResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze DNS records for a website domain",
)
def dns_analysis(
    url: str = Query(
        ...,
        min_length=3,
        description="Website URL or domain to analyze (e.g. https://example.com).",
        examples=["https://example.com"],
    ),
) -> DnsResponse:
    """
    Query DNS records for the domain extracted from the provided website URL.

    Returns A, AAAA, MX, NS, CNAME, and TXT records along with the primary IP address.
    """
    try:
        result = lookup_dns(url)
    except InvalidDomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except DnsDomainNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DnsLookupError as exc:
        logger.exception("DNS endpoint failed for url='%s'", url)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return DnsResponse(**result)
