from typing import Literal

from pydantic import BaseModel, Field


class SslResponse(BaseModel):
    """SSL/TLS certificate analysis results for a website."""

    ssl_status: Literal["Valid", "Invalid"] = Field(
        ...,
        description="Whether the certificate is trusted and currently valid.",
    )
    https_status: Literal["Enabled", "Disabled"] = Field(
        ...,
        description="Whether HTTPS is available on the target host.",
    )
    certificate_issuer: str | None = Field(
        None,
        description="Certificate authority that issued the certificate.",
    )
    subject: str | None = Field(
        None,
        description="Certificate subject distinguished name.",
    )
    valid_from: str | None = Field(
        None,
        description="Certificate validity start date in ISO-8601 format.",
    )
    expiry_date: str | None = Field(
        None,
        description="Certificate expiration date in ISO-8601 format.",
    )
    days_remaining: int | None = Field(
        None,
        description="Number of days until certificate expiration.",
    )
    signature_algorithm: str | None = Field(
        None,
        description="Signature algorithm used by the certificate, when detectable.",
    )
