from pydantic import BaseModel, Field


class WhoisResponse(BaseModel):
    """WHOIS registration details for a website domain."""

    domain_name: str = Field(..., description="Registered domain name.")
    registrar: str | None = Field(None, description="Domain registrar.")
    creation_date: str | None = Field(
        None,
        description="Domain creation date in ISO-8601 format.",
    )
    expiration_date: str | None = Field(
        None,
        description="Domain expiration date in ISO-8601 format.",
    )
    domain_age: str | None = Field(
        None,
        description="Human-readable age of the domain since creation.",
    )
    country: str | None = Field(
        None,
        description="Registrant country, when available from WHOIS.",
    )
