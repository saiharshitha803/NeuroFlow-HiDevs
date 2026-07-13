import uuid

import pytest

from backend.database.connection import db
from backend.database.document_repository import DocumentRepository


@pytest.mark.asyncio
async def test_document_repository():

    await db.connect()

    repo = DocumentRepository()

    # Every test run gets a new hash
    content_hash = str(uuid.uuid4())

    document_id = await repo.create(
        filename="sample.pdf",
        source_type="pdf",
        content_hash=content_hash,
    )

    document = await repo.get(document_id)

    assert document is not None
    assert document["filename"] == "sample.pdf"
    assert document["source_type"] == "pdf"
    assert document["status"] == "queued"

    duplicate = await repo.find_duplicate(content_hash)

    assert duplicate is not None
    assert str(duplicate["id"]) == document_id

    await repo.update_status(
        document_id,
        "processing",
    )

    updated = await repo.get(document_id)

    assert updated["status"] == "processing"

    await repo.delete(document_id)

    deleted = await repo.get(document_id)

    assert deleted is None

    await db.close()