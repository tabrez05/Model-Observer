import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RunCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    model_type: str | None = None
    dataset: str | None = None
    hyperparams: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None


class RunUpdate(BaseModel):
    name: str | None = None
    status: str | None = None
    hyperparams: dict[str, Any] | None = None
    final_metrics: dict[str, Any] | None = None
    tags: list[str] | None = None
    notes: str | None = None


class RunRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    name: str
    model_type: str | None
    dataset: str | None
    status: str
    hyperparams: dict[str, Any]
    final_metrics: dict[str, Any]
    tags: list[str]
    notes: str | None
    duration_seconds: float | None
    created_at: datetime
    completed_at: datetime | None


class RunListResponse(BaseModel):
    total: int
    items: list[RunRead]
