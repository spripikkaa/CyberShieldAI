from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ScanReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    url: str
    prediction: Literal["Legitimate", "Phishing"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime
