import logging

from fastapi import APIRouter, HTTPException, Query, status

from backend.api.schemas.ssl import SslResponse
from backend.cybersecurity.exceptions import InvalidDomainError, SslCertificateError
from backend.cybersecurity.ssl_checker import check_ssl_certificate

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ssl"])


@router.get(
    "/ssl",
    response_model=SslResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze SSL/TLS certificate for a website",
)
def ssl_analysis(
    url: str = Query(
        ...,
        min_length=3,
        description="Website URL or domain to analyze (e.g. https://example.com).",
        examples=["https://example.com"],
    ),
) -> SslResponse:
    """
    Inspect the SSL/TLS certificate for the host extracted from the provided URL.

    Returns HTTPS availability, certificate validity, issuer/subject details,
    expiration information, and signature algorithm when available.
    """
    try:
        result = check_ssl_certificate(url)
    except InvalidDomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except SslCertificateError as exc:
        logger.exception("SSL certificate parsing failed for url='%s'", url)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return SslResponse(**result)
