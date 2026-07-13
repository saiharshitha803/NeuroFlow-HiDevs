import pytest

from backend.database.connection import db


@pytest.mark.asyncio
async def test_database_connection():

    await db.connect()

    async with db.pool.acquire() as conn:

        value = await conn.fetchval(
            "SELECT 1"
        )

        assert value == 1

    await db.close()