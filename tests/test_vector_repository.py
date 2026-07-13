import uuid

import pytest

from backend.database.connection import db
from backend.database.document_repository import DocumentRepository
from backend.database.chunk_repository import ChunkRepository
from backend.retrieval.vector_repository import VectorRepository


@pytest.mark.asyncio
async def test_vector_repository():

    await db.connect()

    doc_repo = DocumentRepository()
    chunk_repo = ChunkRepository()
    vector_repo = VectorRepository()

    document_id = await doc_repo.create(
        filename="sample.pdf",
        source_type="pdf",
        content_hash=str(uuid.uuid4()),
    )

    chunk_id = await chunk_repo.create(
        document_id=document_id,
        chunk_index=0,
        content="Hello NeuroFlow",
        metadata={},
    )

    embedding = [0.1] * 1536

    await vector_repo.upsert_embedding(
        chunk_id,
        embedding,
    )

    results = await vector_repo.similarity_search(
        embedding,
        limit=1,
    )

    assert len(results) == 1
    assert str(results[0]["id"]) == chunk_id

    await doc_repo.delete(document_id)

    await db.close()