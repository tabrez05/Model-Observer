import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"
    __table_args__ = (UniqueConstraint("run_id", "step", name="uq_run_step"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step: Mapped[int] = mapped_column(Integer, nullable=False)
    metrics: Mapped[dict] = mapped_column(JSONB, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    run: Mapped["Run"] = relationship("Run", back_populates="metric_snapshots")  # noqa: F821
