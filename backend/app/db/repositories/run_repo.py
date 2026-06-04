import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.run import Run
from app.schemas.run import RunCreate, RunUpdate


class RunRepository:

    async def create(self, db: AsyncSession, data: RunCreate) -> Run:
        run = Run(**data.model_dump())
        db.add(run)
        await db.flush()
        await db.refresh(run)
        return run

    async def get_by_id(self, db: AsyncSession, run_id: uuid.UUID) -> Run | None:
        result = await db.execute(select(Run).where(Run.id == run_id))
        return result.scalar_one_or_none()

    async def list_runs(
        self,
        db: AsyncSession,
        status: str | None = None,
        tags: list[str] | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[int, list[Run]]:
        query = select(Run)
        if status:
            query = query.where(Run.status == status)
        if tags:
            query = query.where(Run.tags.contains(tags))
        if search:
            query = query.where(Run.name.ilike(f"%{search}%"))
        query = query.order_by(Run.created_at.desc())

        total_q = select(func.count()).select_from(query.subquery())
        total = (await db.execute(total_q)).scalar_one()
        items = (await db.execute(query.offset(offset).limit(limit))).scalars().all()
        return total, list(items)

    async def update(
        self, db: AsyncSession, run: Run, data: RunUpdate
    ) -> Run:
        update_data = data.model_dump(exclude_none=True)
        if "status" in update_data and update_data["status"] in ("completed", "failed"):
            if not run.completed_at:
                run.completed_at = datetime.now(timezone.utc)
            if run.created_at and not run.duration_seconds:
                delta = run.completed_at - run.created_at
                run.duration_seconds = delta.total_seconds()
        for field, value in update_data.items():
            setattr(run, field, value)
        await db.flush()
        await db.refresh(run)
        return run

    async def delete(self, db: AsyncSession, run: Run) -> None:
        await db.delete(run)
        await db.flush()


run_repo = RunRepository()
