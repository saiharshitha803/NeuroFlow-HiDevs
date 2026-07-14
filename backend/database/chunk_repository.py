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


        async with db.pool.acquire() as conn:

            await conn.execute(
                """
                DELETE FROM chunks
                WHERE document_id = $1
                """,
                document_id,
            )



    async def full_text_search(
        self,
        query: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Sparse retrieval using PostgreSQL Full Text Search.
        """

        async with db.pool.acquire() as conn:

            rows = await conn.fetch(
                """
                SELECT
                    *,
                    ts_rank_cd(
                        to_tsvector('english', content),
                        plainto_tsquery('english', $1)
                    ) AS sparse_score

                FROM chunks

                WHERE
                    to_tsvector('english', content)
                    @@
                    plainto_tsquery('english', $1)

                ORDER BY sparse_score DESC

                LIMIT $2
                """,
                query,
                limit,
            )


        return [dict(row) for row in rows]



    async def metadata_search(
        self,
        filters: dict[str, Any],
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Metadata retrieval using JSONB filtering.

        Example:

        {
            "year": 2023,
            "topic": "climate"
        }

        Uses PostgreSQL JSONB containment:
        
        metadata @> jsonb
        """

        if not filters:

            return []


        async with db.pool.acquire() as conn:

            rows = await conn.fetch(
                """
                SELECT *
                FROM chunks

                WHERE metadata @> $1::jsonb

                LIMIT $2
                """,
                json.dumps(filters),
                limit,
            )


        return [dict(row) for row in rows]