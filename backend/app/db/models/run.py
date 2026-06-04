import uuid
from datetime import datetime, timezone

from sqlalchemy import ARRAY, DateTime, Enum, Float, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class RunStatus(str):
    QUEUED    = "queued"
    RUNNING   = "running"
    COMPLETED = "completed"
    FAILED    = "failed"


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_type: Mapped[str | None] = mapped_column(String(100))
    dataset: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        Enum("queued", "running", "completed", "failed", name="run_status"),
        default="queued",
        nullable=False,
    )
    hyperparams: Mapped[dict] = mapped_column(JSONB, default=dict)
    final_metrics: Mapped[dict] = mapped_column(JSONB, default=dict)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    notes: Mapped[str | None] = mapped_column(Text)
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    metric_snapshots: Mapped[list["MetricSnapshot"]] = relationship(  # noqa: F821
        "MetricSnapshot", back_populates="run", cascade="all, delete-orphan"
    )
    artifacts: Mapped[list["Artifact"]] = relationship(  # noqa: F821
        "Artifact", back_populates="run", cascade="all, delete-orphan"
    )
