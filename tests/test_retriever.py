import uuid

import pytest

from backend.database.connection import db
from backend.database.document_repository import DocumentRepository
from backend.database.chunk_repository import ChunkRepository
from backend.retrieval.vector_repository import VectorRepository
from backend.retrieval.retriever import Retriever


@pytest.mark.asyncio
async def test_retriever():

    await db.connect()

    doc_repo = DocumentRepository()
    chunk_repo = ChunkRepository()
    vector_repo = VectorRepository()
    retriever = Retriever()

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

    results = await retriever.retrieve(
        embedding,
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["content"] == "Hello NeuroFlow"

    await db.close()