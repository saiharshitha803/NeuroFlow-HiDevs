from typing import Any

from backend.database.connection import db


class VectorRepository:
    """
    Repository for storing and searching embeddings.
    """

    async def upsert_embedding(
        self,
        chunk_id: str,
        embedding: list[float],
    ) -> None:
        # Ensure database is connected
        if db.pool is None:
            await db.connect()

        # Convert Python list -> pgvector format
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

        async with db.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE chunks
                SET embedding = $1::vector
                WHERE id = $2
                """,
                embedding_str,
                chunk_id,
            )

    async def similarity_search(
        self,
        embedding: list[float],
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        # Ensure database is connected
        if db.pool is None:
            await db.connect()

        # Convert Python list -> pgvector format
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

        async with db.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT *
                FROM chunks
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> $1::vector
                LIMIT $2
                """,
                embedding_str,
                limit,
            )

        return [dict(row) for row in rows]