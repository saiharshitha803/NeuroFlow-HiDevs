import asyncio
import json

import redis.asyncio as redis

from backend.config import settings


MODELS = [
    {
        "model": "gpt-4o-mini",
        "provider": "openai",
        "task_type": "generation",
        "estimated_cost": 0.001,
        "vision": False,
        "context": 128000,
        "fine_tuned": False,
        "judge": False,
    },
    {
        "model": "gpt-4o",
        "provider": "openai",
        "task_type": "generation",
        "estimated_cost": 0.01,
        "vision": True,
        "context": 128000,
        "fine_tuned": False,
        "judge": False,
    },
    {
        "model": "claude-3-haiku",
        "provider": "anthropic",
        "task_type": "generation",
        "estimated_cost": 0.002,
        "vision": True,
        "context": 200000,
        "fine_tuned": False,
        "judge": False,
    },
]


async def main():

    client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
    )

    await client.set(
        "router:models",
        json.dumps(MODELS),
    )

    print("✅ Router models loaded into Redis.")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())