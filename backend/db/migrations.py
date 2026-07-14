from backend.database.connection import db


async def run_migrations():
    """
    Apply database migrations.

    Handles:
    - metadata JSONB column
    - metadata GIN index
    """

    async with db.pool.acquire() as conn:

        # Add metadata column for hybrid retrieval filtering
        await conn.execute(
            """
            ALTER TABLE chunks
            ADD COLUMN IF NOT EXISTS metadata JSONB
            DEFAULT '{}'::jsonb;
            """
        )


        # Add GIN index for fast JSONB filtering
        await conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_chunks_metadata
            ON chunks
            USING GIN(metadata);
            """
        )


        print("Migrations completed successfully.")