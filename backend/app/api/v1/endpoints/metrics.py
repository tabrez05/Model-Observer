import uuid

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_redis
from app.db.repositories.metric_repo import metric_repo
from app.db.repositories.run_repo import run_repo
from app.db.session import get_db
from app.schemas.metric import MetricCreate, MetricRead
from app.services import stream_service

router = APIRouter(tags=["metrics"])


@router.post("/runs/{run_id}/metrics", status_code=201)
async def log_metric(
    run_id: uuid.UUID,
    payload: MetricCreate,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    run = await run_repo.get_by_id(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    # 1. Push to Redis stream (live delivery to SSE consumers)
    await stream_service.push_metric(redis, str(run_id), payload.step, payload.metrics)

    # 2. Persist to PostgreSQL
    snapshot = await metric_repo.create(db, run_id, payload)

    # 3. Auto-transition status queued→running on first metric
    if run.status == "queued":
        from app.schemas.run import RunUpdate
        await run_repo.update(db, run, RunUpdate(status="running"))

    return {"ok": True, "step": payload.step}


@router.get("/runs/{run_id}/metrics", response_model=list[MetricRead])
async def get_metric_history(
    run_id: uuid.UUID,
    from_step: int = Query(0, ge=0),
    to_step: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    run = await run_repo.get_by_id(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return await metric_repo.get_history(db, run_id, from_step, to_step)


@router.get("/runs/{run_id}/stream")
async def stream_metrics(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """Server-Sent Events endpoint — streams live metrics to the browser."""
    run = await run_repo.get_by_id(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    replay = run.status in ("completed", "failed")

    return StreamingResponse(
        stream_service.sse_metric_generator(redis, str(run_id), start_from_beginning=replay),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disable nginx buffering
            "Connection": "keep-alive",
        },
    )
