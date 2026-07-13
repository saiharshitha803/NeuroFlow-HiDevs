import uuid

import pytest

from backend.database.connection import db
from backend.database.document_repository import DocumentRepository
from backend.database.chunk_repository import ChunkRepository


@pytest.mark.asyncio
async def test_chunk_repository():

    await db.connect()

    doc_repo = DocumentRepository()
    chunk_repo = ChunkRepository()

    document_id = await doc_repo.create(
        filename="sample.pdf",
        source_type="pdf",
        content_hash=str(uuid.uuid4()),
    )

    await chunk_repo.create(
        document_id=document_id,
        chunk_index=0,
        content="Hello World",
        metadata={"page": 1},
    )

    await chunk_repo.create(
        document_id=document_id,
        chunk_index=1,
        content="Second Chunk",
        metadata={"page": 2},
    )

    chunks = await chunk_repo.list_chunks(document_id)

    assert len(chunks) == 2
    assert chunks[0]["content"] == "Hello World"

    count = await chunk_repo.count(document_id)

    assert count == 2

    await chunk_repo.delete(document_id)

    assert await chunk_repo.count(document_id) == 0

    await doc_repo.delete(document_id)

    await db.close()