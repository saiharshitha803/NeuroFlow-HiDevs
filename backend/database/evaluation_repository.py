import uuid
from typing import Any

from backend.database.connection import db


class EvaluationRepository:
    """
    Repository for storing and retrieving evaluation results.
    """

    async def create(
        self,
        run_id: str,
        faithfulness: float,
        answer_relevance: float,
        context_precision: float,
        context_recall: float,
        overall_score: float,
        judge_model: str,
        user_rating: int,
    ) -> str:

        evaluation_id = str(uuid.uuid4())

        async with db.pool.acquire() as conn:

            await conn.execute(
                """
                INSERT INTO evaluations
                (
                    id,
                    run_id,
                    faithfulness,
                    answer_relevance,
                    context_precision,
                    context_recall,
                    overall_score,
                    judge_model,
                    user_rating
                )
                VALUES
                ($1,$2,$3,$4,$5,$6,$7,$8,$9)
                """,
                evaluation_id,
                run_id,
                faithfulness,
                answer_relevance,
                context_precision,
                context_recall,
                overall_score,
                judge_model,
                user_rating,
            )

        return evaluation_id

    async def get(
        self,
        evaluation_id: str,
    ) -> dict[str, Any] | None:

        async with db.pool.acquire() as conn:

            row = await conn.fetchrow(
                """
                SELECT *
                FROM evaluations
                WHERE id=$1
                """,
                evaluation_id,
            )

        return dict(row) if row else None

    async def list(self) -> list[dict[str, Any]]:

        async with db.pool.acquire() as conn:

            rows = await conn.fetch(
                """
                SELECT *
                FROM evaluations
                ORDER BY evaluated_at DESC
                """
            )

        return [dict(row) for row in rows]

    async def delete(
        self,
        evaluation_id: str,
    ) -> None:

        async with db.pool.acquire() as conn:

            await conn.execute(
                """
                DELETE FROM evaluations
                WHERE id=$1
                """,
                evaluation_id,
            )