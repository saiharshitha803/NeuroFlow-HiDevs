import json
import uuid
from typing import Any

from backend.database.connection import db


class PipelineRepository:
    """
    Repository for managing RAG pipelines.
    """

    async def create(
        self,
        name: str,
        config: dict[str, Any],
    ) -> str:

        pipeline_id = str(uuid.uuid4())

        async with db.pool.acquire() as conn:

            await conn.execute(
                """
                INSERT INTO pipelines
                (
                    id,
                    name,
                    config
                )
                VALUES
                ($1,$2,$3::jsonb)
                """,
                pipeline_id,
                name,
                json.dumps(config),
            )

        return pipeline_id

    async def get(
        self,
        pipeline_id: str,
    ) -> dict[str, Any] | None:

        async with db.pool.acquire() as conn:

            row = await conn.fetchrow(
                """
                SELECT *
                FROM pipelines
                WHERE id=$1
                """,
                pipeline_id,
            )

        return dict(row) if row else None

    async def list(self) -> list[dict[str, Any]]:

        async with db.pool.acquire() as conn:

            rows = await conn.fetch(
                """
                SELECT *
                FROM pipelines
                ORDER BY created_at
                """
            )

        return [dict(row) for row in rows]

    async def delete(
        self,
        pipeline_id: str,
    ) -> None:

        async with db.pool.acquire() as conn:

            await conn.execute(
                """
                DELETE FROM pipelines
                WHERE id=$1
                """,
                pipeline_id,
            )