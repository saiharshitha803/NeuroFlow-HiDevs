import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect(
        host="127.0.0.1",
        port=5432,
        user="neuroflow",
        password="neuroflow123",
        database="neuroflow",
        ssl=False,
    )

    result = await conn.fetchval("SELECT version()")
    print(result)

    await conn.close()

asyncio.run(test())