import json
from uuid import UUID

from backend.database.connection import db


class EvaluationRepository:
    """
    Handles evaluation persistence.
    """

    def __init__(self):
        self.db = db

    async def create_evaluation(
        self,
        run_id,
        faithfulness,
        answer_relevance,
        context_precision,
        context_recall,
        overall_score,
        judge_model,
    ):

        sql = """
        INSERT INTO evaluations
        (
            run_id,
            faithfulness,
            answer_relevance,
            context_precision,
            context_recall,
            overall_score,
            judge_model
        )
        VALUES
        ($1,$2,$3,$4,$5,$6,$7)
        """

        async with self.db.pool.acquire() as conn:

            await conn.execute(
                sql,
                run_id,
                faithfulness,
                answer_relevance,
                context_precision,
                context_recall,
                overall_score,
                judge_model,
            )

    async def get_evaluation(
        self,
        run_id: UUID,
    ):

        sql = """
        SELECT *
        FROM evaluations
        WHERE run_id=$1
        """

        async with self.db.pool.acquire() as conn:

            row = await conn.fetchrow(
                sql,
                run_id,
            )

        return dict(row) if row else None

    async def update_user_rating(
        self,
        run_id: UUID,
        rating: int,
    ):

        sql = """
        UPDATE evaluations
        SET user_rating=$2
        WHERE run_id=$1
        """

        async with self.db.pool.acquire() as conn:

            await conn.execute(
                sql,
                run_id,
                rating,
            )

    async def update_metadata(
        self,
        run_id: UUID,
        metadata: dict,
    ):

        sql = """
        UPDATE evaluations
        SET metadata=$2::jsonb
        WHERE run_id=$1
        """

        async with self.db.pool.acquire() as conn:

            await conn.execute(
                sql,
                run_id,
                json.dumps(metadata),   # <-- FIX
            )