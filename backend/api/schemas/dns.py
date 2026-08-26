from pydantic import BaseModel, Field


class DnsResponse(BaseModel):
    """DNS record analysis results for a website domain."""

    domain_name: str = Field(..., description="Domain name that was analyzed.")
    ip_address: str | None = Field(
        None,
        description="Primary IPv4 address resolved for the domain, when available.",
    )
    a_records: list[str] = Field(
        default_factory=list,
        description="IPv4 A records for the domain.",
    )
    aaaa_records: list[str] = Field(
        default_factory=list,
        description="IPv6 AAAA records for the domain.",
    )
    mx_records: list[str] = Field(
        default_factory=list,
        description="Mail exchange (MX) records with preference and host.",
    )
    ns_records: list[str] = Field(
        default_factory=list,
        description="Nameserver (NS) records for the domain.",
    )
    cname: list[str] = Field(
        default_factory=list,
        description="Canonical name (CNAME) records for the domain.",
    )
    txt_records: list[str] = Field(
        default_factory=list,
        description="Text (TXT) records associated with the domain.",
    )
