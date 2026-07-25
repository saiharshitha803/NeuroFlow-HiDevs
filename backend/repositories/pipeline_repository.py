import json
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
        description: str,
        config: dict,
    ) -> UUID:
        """
        Create a new pipeline.
        """

        sql = """
        INSERT INTO pipelines
        (
            name,
            description,
            config,
            version,
            status
        )
        VALUES
        (
            $1,
            $2,
            $3::jsonb,
            1,
            'active'
        )
        RETURNING id
        """

        async with self.db.pool.acquire() as conn:

            row = await conn.fetchrow(
                sql,
                name,
                description,
                json.dumps(config),
            )

        return row["id"]

    async def list_pipelines(self):
        """
        List all active pipelines.
        """

        sql = """
        SELECT *
        FROM pipelines
        WHERE status <> 'archived'
        ORDER BY created_at DESC
        """

        async with self.db.pool.acquire() as conn:
            return await conn.fetch(sql)

    async def get_pipeline(
        self,
        pipeline_id: UUID,
    ):
        """
        Fetch pipeline by ID.
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
        Fetch latest pipeline by name.
        """

        sql = """
        SELECT *
        FROM pipelines
        WHERE name=$1
        ORDER BY version DESC
        LIMIT 1
        """

        async with self.db.pool.acquire() as conn:

            return await conn.fetchrow(
                sql,
                name,
            )

    async def get_latest_pipeline(
        self,
        name: str,
    ):
        """
        Get latest pipeline version.
        """

        sql = """
        SELECT *
        FROM pipelines
        WHERE name=$1
        ORDER BY version DESC
        LIMIT 1
        """

        async with self.db.pool.acquire() as conn:

            return await conn.fetchrow(
                sql,
                name,
            )

    async def get_versions(
        self,
        name: str,
    ):
        """
        Get all versions.
        """

        sql = """
        SELECT *
        FROM pipelines
        WHERE name=$1
        ORDER BY version DESC
        """

        async with self.db.pool.acquire() as conn:

            return await conn.fetch(
                sql,
                name,
            )

    async def update_pipeline(
        self,
        pipeline_id: UUID,
        config: dict,
    ) -> UUID:
        """
        Create a new version of an existing pipeline.
        """

        pipeline = await self.get_pipeline(
            pipeline_id,
        )

        if pipeline is None:
            raise ValueError("Pipeline not found.")

        sql = """
        INSERT INTO pipelines
        (
            name,
            description,
            config,
            version,
            status
        )
        VALUES
        (
            $1,
            $2,
            $3::jsonb,
            $4,
            'active'
        )
        RETURNING id
        """

        async with self.db.pool.acquire() as conn:

            row = await conn.fetchrow(
                sql,
                pipeline["name"],
                config["description"],
                json.dumps(config),
                pipeline["version"] + 1,
            )

        return row["id"]

    async def archive_pipeline(
        self,
        pipeline_id: UUID,
    ):
        """
        Soft delete a pipeline.
        """

        sql = """
        UPDATE pipelines
        SET
            status='archived',
            updated_at=NOW()
        WHERE id=$1
        """

        async with self.db.pool.acquire() as conn:

            await conn.execute(
                sql,
                pipeline_id,
            )