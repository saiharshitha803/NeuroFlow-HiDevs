import redis.asyncio as redis
import asyncpg
import mlflow


async def check_postgres(pool):
    try:
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return True
    except Exception:
        return False


async def check_redis(host, port, password):
    try:
        client = redis.Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True,
        )

        await client.ping()
        await client.close()

        return True

    except Exception:
        return False


async def check_mlflow():
    try:
        mlflow.search_experiments()

        return True

    except Exception:
        return False