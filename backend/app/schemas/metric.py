import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MetricCreate(BaseModel):
    step: int = Field(..., ge=0)
    metrics: dict[str, float] = Field(..., min_length=1)


class MetricRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    run_id: uuid.UUID
    step: int
    metrics: dict[str, Any]
    recorded_at: datetime
