from uuid import UUID

from backend.database.connection import db


class PipelineRepository:
    """
    Handles pipeline persistence.
    """

    def __init__(self):
        self.db = db

    async def create_pipeline(
        self,
        name: str,
        config: dict | None = None,
    ) -> UUID:
        """
        Create a new pipeline and return its ID.
        """

        sql = """
        INSERT INTO pipelines
        (
            name,
            config
        )
        VALUES
        ($1, $2)
        RETURNING id
        """

        async with self.db.pool.acquire() as conn:

            row = await conn.fetchrow(
                sql,
                name,
                config or {},
            )

        return row["id"]

    async def get_pipeline(
        self,
        pipeline_id: UUID,
    ):
        """
        Fetch a pipeline by ID.
        """

        sql = """
        SELECT *
        FROM pipelines
        WHERE id=$1
        """

        async with self.db.pool.acquire() as conn:

            return await conn.fetchrow(
                sql,
                pipeline_id,
            )

    async def get_pipeline_by_name(
        self,
        name: str,
    ):
        """
        Fetch pipeline by name.
        """

        sql = """
        SELECT *
        FROM pipelines
        WHERE name=$1
        """

        async with self.db.pool.acquire() as conn:

            return await conn.fetchrow(
                sql,
                name,
            )