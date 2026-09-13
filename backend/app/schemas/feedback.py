import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreateRequest(BaseModel):
    scan_id: uuid.UUID = Field(..., description="ID of the scan being evaluated")
    feedback: str = Field(..., min_length=2, max_length=2000, description="Analyst feedback or tuning commentary")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Optional 1-5 rating score")


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    scan_id: uuid.UUID
    feedback: str
    created_at: datetime
