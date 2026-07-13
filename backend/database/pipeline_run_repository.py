import uuid
import json
from typing import Any

from backend.database.connection import db


class PipelineRunRepository:
    """
    Repository for storing and retrieving pipeline runs.
    """

    async def create(
        self,
        pipeline_id: str,
        query: str,
        retrieved_chunk_ids: list[str] | None = None,
        generation: str | None = None,
        latency_ms: int | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        model_used: str | None = None,
        status: str = "running",
    ) -> str:
        """
        Create a pipeline run.
        """

        run_id = str(uuid.uuid4())

        async with db.pool.acquire() as conn:

            await conn.execute(
                """
                INSERT INTO pipeline_runs
                (
                    id,
                    pipeline_id,
                    query,
                    retrieved_chunk_ids,
                    generation,
                    latency_ms,
                    input_tokens,
                    output_tokens,
                    model_used,
                    status
                )
                VALUES
                ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
                """,
                run_id,
                pipeline_id,
                query,
                retrieved_chunk_ids,
                generation,
                latency_ms,
                input_tokens,
                output_tokens,
                model_used,
                status,
            )

        return run_id

    async def get(
        self,
        run_id: str,
    ) -> dict[str, Any] | None:

        async with db.pool.acquire() as conn:

            row = await conn.fetchrow(
                """
                SELECT *
                FROM pipeline_runs
                WHERE id=$1
                """,
                run_id,
            )

        return dict(row) if row else None

    async def list(self) -> list[dict[str, Any]]:

        async with db.pool.acquire() as conn:

            rows = await conn.fetch(
                """
                SELECT *
                FROM pipeline_runs
                ORDER BY created_at DESC
                """
            )

        return [dict(row) for row in rows]

    async def update_status(
        self,
        run_id: str,
        status: str,
    ) -> None:

        async with db.pool.acquire() as conn:

            await conn.execute(
                """
                UPDATE pipeline_runs
                SET status=$1
                WHERE id=$2
                """,
                status,
                run_id,
            )

    async def delete(
        self,
        run_id: str,
    ) -> None:

        async with db.pool.acquire() as conn:

            await conn.execute(
                """
                DELETE FROM pipeline_runs
                WHERE id=$1
                """,
                run_id,
            )