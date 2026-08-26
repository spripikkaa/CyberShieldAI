from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserDocument(BaseModel):
    """MongoDB User collection document."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the user account was created.",
    )

    def to_mongo(self) -> dict:
        return self.model_dump()
