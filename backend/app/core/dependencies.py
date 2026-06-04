from typing import AsyncGenerator

import redis.asyncio as aioredis

from app.core.config import settings

_redis_pool: aioredis.Redis | None = None


async def get_redis_pool() -> aioredis.Redis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False,
        )
    return _redis_pool


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    pool = await get_redis_pool()
    yield pool
