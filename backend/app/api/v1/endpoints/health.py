import redis.asyncio as aioredis
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_redis
from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    db_status, redis_status = "connected", "connected"

    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    try:
        await redis.ping()
    except Exception:
        redis_status = "error"

    overall = "ok" if db_status == "connected" and redis_status == "connected" else "degraded"
    return {
        "status": overall,
        "db": db_status,
        "redis": redis_status,
        "version": "0.1.0",
    }
