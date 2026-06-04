import asyncio
import json
import time

import redis.asyncio as aioredis

from app.core.config import settings


def _stream_key(run_id: str) -> str:
    return f"experiment:{run_id}:metrics"


async def push_metric(redis: aioredis.Redis, run_id: str, step: int, metrics: dict) -> None:
    """Write one metric entry to the Redis stream for a run."""
    payload = {"step": str(step), "ts": str(time.time())}
    payload.update({k: str(v) for k, v in metrics.items()})
    await redis.xadd(
        _stream_key(run_id),
        payload,
        maxlen=settings.REDIS_STREAM_MAXLEN,
        approximate=True,
    )


async def read_history(
    redis: aioredis.Redis, run_id: str, from_id: str = "0"
) -> list[dict]:
    """Read all entries in a stream starting from from_id."""
    entries = await redis.xrange(_stream_key(run_id), min=from_id)
    result = []
    for entry_id, fields in entries:
        parsed = {k.decode(): v.decode() for k, v in fields.items()}
        result.append({"_id": entry_id.decode(), **parsed})
    return result


async def sse_metric_generator(redis: aioredis.Redis, run_id: str, start_from_beginning: bool = False):
    """
    Async generator yielding SSE-formatted strings.
    If start_from_beginning=True, replays full history first.
    Then streams new events as they arrive.
    """
    last_id = "0" if start_from_beginning else "$"

    while True:
        try:
            messages = await redis.xread(
                {_stream_key(run_id): last_id},
                block=int(settings.SSE_HEARTBEAT_INTERVAL * 1000),
                count=50,
            )
        except asyncio.CancelledError:
            return

        if messages:
            for _, entries in messages:
                for entry_id, fields in entries:
                    last_id = entry_id.decode() if isinstance(entry_id, bytes) else entry_id
                    data = {
                        k.decode() if isinstance(k, bytes) else k:
                        v.decode() if isinstance(v, bytes) else v
                        for k, v in fields.items()
                    }
                    yield f"event: metric\ndata: {json.dumps(data)}\n\n"
        else:
            yield f"event: heartbeat\ndata: {json.dumps({'ts': time.time()})}\n\n"


async def delete_stream(redis: aioredis.Redis, run_id: str) -> None:
    await redis.delete(_stream_key(run_id))
