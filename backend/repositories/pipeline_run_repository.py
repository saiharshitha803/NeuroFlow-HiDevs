from typing import Any
from uuid import UUID

from backend.database.connection import db


class PipelineRunRepository:
    """
   Handles pipeline run persistence.
    """

    def __init__(self):
        self.db = db

    async def create_run(
        self,
        pipeline_id: UUID,
        query: str,
        prompt: str,
        retrieved_chunk_ids: list | None = None,
    ) -> UUID:

        sql = """
        INSERT INTO pipeline_runs
        (
            pipeline_id,
            query,
            prompt,
            retrieved_chunk_ids,
            status
        )
        VALUES
        ($1,$2,$3,$4,$5)
        RETURNING id
        """

        async with self.db.pool.acquire() as conn:

            row = await conn.fetchrow(
                sql,
                pipeline_id,
                query,
                prompt,
                retrieved_chunk_ids,
                "running",
            )

        return row["id"]

    async def update_run(
        self,
        run_id: UUID,
        **kwargs: Any,
    ):

        if not kwargs:
            return

        fields = []
        values = []

        for index, (key, value) in enumerate(
            kwargs.items(),
            start=2,
        ):
            fields.append(f"{key}=${index}")
            values.append(value)

        sql = f"""
        UPDATE pipeline_runs
        SET {", ".join(fields)}
        WHERE id=$1
        """

        async with self.db.pool.acquire() as conn:

            await conn.execute(
                sql,
                run_id,
                *values,
            )