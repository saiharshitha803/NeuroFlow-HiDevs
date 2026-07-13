import asyncio
import redis.asyncio as redis

async def test():
    client = redis.Redis(
        host="127.0.0.1",
        port=6379,
        password="redis123",
        decode_responses=True,
    )

    print(await client.ping())

    await client.aclose()

asyncio.run(test())