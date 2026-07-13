import asyncio
import asyncpg

from backend.config import settings


class Database:
    def __init__(self):
        self.pool = None
        self.loop = None

    async def connect(self):
        current_loop = asyncio.get_running_loop()

        # Create a new pool if:
        # - no pool exists
        # - the old loop is different
        # - the pool was closed
        if (
            self.pool is None
            or self.loop != current_loop
            or self.pool._closed
        ):
            if self.pool is not None:
                try:
                    await self.pool.close()
                except Exception:
                    pass

            print("Connecting to PostgreSQL...")
            print("HOST:", settings.POSTGRES_HOST)
            print("PORT:", settings.POSTGRES_PORT)
            print("USER:", settings.POSTGRES_USER)
            print("DB:", settings.POSTGRES_DB)

            self.pool = await asyncpg.create_pool(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
                ssl=False,
                min_size=1,
                max_size=5,
            )

            self.loop = current_loop

            print("Connected!")

    async def disconnect(self):
        if self.pool is not None:
            try:
                await self.pool.close()
            except Exception:
                pass

            self.pool = None
            self.loop = None

    async def close(self):
        await self.disconnect()


db = Database()