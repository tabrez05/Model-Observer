import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.metric_snapshot import MetricSnapshot
from app.schemas.metric import MetricCreate


class MetricRepository:

    async def create(
        self, db: AsyncSession, run_id: uuid.UUID, data: MetricCreate
    ) -> MetricSnapshot:
        snapshot = MetricSnapshot(
            run_id=run_id, step=data.step, metrics=data.metrics
        )
        db.add(snapshot)
        await db.flush()
        await db.refresh(snapshot)
        return snapshot

    async def bulk_upsert(
        self,
        db: AsyncSession,
        run_id: uuid.UUID,
        snapshots: list[dict],
    ) -> None:
        """Insert many metric snapshots, skip duplicates (on conflict do nothing)."""
        if not snapshots:
            return
        stmt = pg_insert(MetricSnapshot).values(
            [{"run_id": run_id, **s} for s in snapshots]
        )
        stmt = stmt.on_conflict_do_nothing(index_elements=["run_id", "step"])
        await db.execute(stmt)
        await db.flush()

    async def get_history(
        self,
        db: AsyncSession,
        run_id: uuid.UUID,
        from_step: int = 0,
        to_step: int | None = None,
    ) -> list[MetricSnapshot]:
        q = (
            select(MetricSnapshot)
            .where(MetricSnapshot.run_id == run_id)
            .where(MetricSnapshot.step >= from_step)
            .order_by(MetricSnapshot.step)
        )
        if to_step is not None:
            q = q.where(MetricSnapshot.step <= to_step)
        result = await db.execute(q)
        return list(result.scalars().all())


metric_repo = MetricRepository()
