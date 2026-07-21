import json

import redis.asyncio as redis

from backend.config import settings


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
)


async def enqueue_evaluation(run_id):

    await redis_client.lpush(
        "evaluation_jobs",
        json.dumps(
            {
                "run_id": str(run_id)
            }
        ),
    )