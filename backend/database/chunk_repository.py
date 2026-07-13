import json
import uuid
from typing import Any

from backend.database.connection import db


class ChunkRepository:
    """
   Repository for storing and retrieving document chunks.
    """

    async def create(
        self,
        document_id: str,
        chunk_index: int,
        content: str,
        metadata: dict[str, Any],
    ) -> str:
        """
        Insert a new chunk into the database.
        """

        chunk_id = str(uuid.uuid4())
        token_count = len(content.split())

        async with db.pool.acquire() as conn:

            await conn.execute(
                """
                INSERT INTO chunks
                (
                    id,
                    document_id,
                    content,
                    chunk_index,
                    token_count,
                    metadata
                )
                VALUES
                ($1, $2, $3, $4, $5, $6::jsonb)
                """,
                chunk_id,
                document_id,
                content,
                chunk_index,
                token_count,
                json.dumps(metadata),
            )

        return chunk_id

    async def list_chunks(
        self,
        document_id: str,
    ) -> list[dict[str, Any]]:
        """
        Return all chunks belonging to a document.
        """

        async with db.pool.acquire() as conn:

            rows = await conn.fetch(
                """
                SELECT *
                FROM chunks
                WHERE document_id = $1
                ORDER BY chunk_index
                """,
                document_id,
            )

        return [dict(row) for row in rows]

    async def count(
        self,
        document_id: str,
    ) -> int:
        """
        Return number of chunks for a document.
        """

        async with db.pool.acquire() as conn:

            return await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM chunks
                WHERE document_id = $1
                """,
                document_id,
            )

    async def delete(
        self,
        document_id: str,
    ) -> None:
        """
        Delete all chunks for a document.
        """

        async with db.pool.acquire() as conn:

            await conn.execute(
                """
                DELETE FROM chunks
                WHERE document_id = $1
                """,
                document_id,
            )