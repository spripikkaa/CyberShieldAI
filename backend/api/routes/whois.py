import logging

from fastapi import APIRouter, HTTPException, Query, status

from backend.api.schemas.whois import WhoisResponse
from backend.cybersecurity.exceptions import (
    InvalidDomainError,
    WhoisDomainNotFoundError,
    WhoisLookupError,
)
from backend.cybersecurity.whois_checker import lookup_whois

logger = logging.getLogger(__name__)

router = APIRouter(tags=["whois"])


@router.get(
    "/whois",
    response_model=WhoisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze domain registration details via WHOIS",
)
def whois_analysis(
    url: str = Query(
        ...,
        min_length=3,
        description="Website URL or domain to analyze (e.g. https://example.com).",
        examples=["https://example.com"],
    ),
) -> WhoisResponse:
    """
    Look up WHOIS records for the domain extracted from the provided website URL.

    Returns registration metadata including registrar, creation/expiration dates,
    domain age, and country when available.
    """
    try:
        result = lookup_whois(url)
    except InvalidDomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except WhoisDomainNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except WhoisLookupError as exc:
        logger.exception("WHOIS endpoint failed for url='%s'", url)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return WhoisResponse(**result)
