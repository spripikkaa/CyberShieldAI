from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ScanReportDocument(BaseModel):
    """MongoDB ScanReports collection document."""

    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(..., min_length=1, description="MongoDB ObjectId of the user.")
    url: str = Field(..., min_length=3)
    prediction: Literal["Legitimate", "Phishing"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the scan was performed.",
    )

    def to_mongo(self) -> dict:
        return self.model_dump()
