from uuid import UUID

from backend.database.connection import db


class TrainingPairRepository:
    """
    Stores high-quality conversations.
    """

    def __init__(self):
        self.db = db

    async def create(
        self,
        run_id: UUID,
        system_prompt: str,
        user_message: str,
        assistant_message: str,
        quality_score: float,
    ):

        sql = """
        INSERT INTO training_pairs
        (
            run_id,
            system_prompt,
            user_message,
            assistant_message,
            quality_score
        )
        VALUES
        ($1,$2,$3,$4,$5)
        """

        async with self.db.pool.acquire() as conn:

            await conn.execute(
                sql,
                run_id,
                system_prompt,
                user_message,
                assistant_message,
                quality_score,
            )