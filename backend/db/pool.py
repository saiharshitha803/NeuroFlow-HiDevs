import asyncpg

pool = None


async def create_pool(database_url: str):
    global pool

    pool = await asyncpg.create_pool(
        database_url,
        min_size=2,
        max_size=10,
    )

    return pool


async def close_pool():
    global pool

    if pool:
        await pool.close()