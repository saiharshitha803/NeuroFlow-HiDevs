import hashlib
from typing import Any

import asyncpg


async def compute_sha256(
    file_bytes: bytes,
) -> str:
    """
    Compute SHA-256 hash of a file.

    Args:
        file_bytes: Raw bytes of the uploaded file.

    Returns:
        Hexadecimal SHA-256 hash.
    """

    sha = hashlib.sha256()

    sha.update(file_bytes)

    return sha.hexdigest()


async def check_duplicate(
    conn: asyncpg.Connection,
    content_hash: str,
) -> dict[str, Any] | None:
    """
    Check whether a document with the same content hash
    already exists.

    Returns:
        Existing document row or None.
    """

    row = await conn.fetchrow(
        """
        SELECT
            document_id,
            status,
            metadata
        FROM documents
        WHERE content_hash = $1
        """,
        content_hash,
    )

    if row is None:
        return None

    return dict(row)


async def register_document_hash(
    conn: asyncpg.Connection,
    document_id: str,
    content_hash: str,
) -> None:
    """
    Save the content hash for a document.
    """

    await conn.execute(
        """
        UPDATE documents
        SET content_hash = $1
        WHERE document_id = $2
        """,
        content_hash,
        document_id,
    )