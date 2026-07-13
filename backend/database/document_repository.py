import uuid
from typing import Any

from backend.database.connection import db


class DocumentRepository:

    async def create(
        self,
        filename: str,
        source_type: str,
        content_hash: str,
    ) -> str:
        """
        Create a new document.
        """

        document_id = str(uuid.uuid4())

        async with db.pool.acquire() as conn:

            await conn.execute(
                """
                INSERT INTO documents
                (
                    id,
                    filename,
                    source_type,
                    content_hash,
                    status
                )
                VALUES
                ($1, $2, $3, $4, 'queued')
                """,
                document_id,
                filename,
                source_type,
                content_hash,
            )

        return document_id

    async def get(
        self,
        document_id: str,
    ) -> dict[str, Any] | None:

        async with db.pool.acquire() as conn:

            row = await conn.fetchrow(
                """
                SELECT *
                FROM documents
                WHERE id=$1
                """,
                document_id,
            )

        return dict(row) if row else None

    async def find_duplicate(
        self,
        content_hash: str,
    ) -> dict[str, Any] | None:

        async with db.pool.acquire() as conn:

            row = await conn.fetchrow(
                """
                SELECT *
                FROM documents
                WHERE content_hash=$1
                """,
                content_hash,
            )

        return dict(row) if row else None

    async def update_status(
        self,
        document_id: str,
        status: str,
    ) -> None:

        async with db.pool.acquire() as conn:

            await conn.execute(
                """
                UPDATE documents
                SET status=$1
                WHERE id=$2
                """,
                status,
                document_id,
            )

    async def delete(
        self,
        document_id: str,
    ) -> None:

        async with db.pool.acquire() as conn:

            await conn.execute(
                """
                DELETE FROM documents
                WHERE id=$1
                """,
                document_id,
            )