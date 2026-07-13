import pytest
import redis.asyncio as redis

from pipelines.ingestion.queue import (
    IngestionQueue,
)


@pytest.mark.asyncio
async def test_queue():

    client = redis.Redis()

    queue = IngestionQueue(client)

    await queue.enqueue(
        "doc1",
        "/tmp/file.pdf",
        "pdf",
    )

    job = await queue.dequeue()

    assert job["document_id"] == "doc1"

    assert job["source_type"] == "pdf"



import pytest
import redis.asyncio as redis

from pipelines.ingestion.queue import IngestionQueue


@pytest.mark.asyncio
async def test_queue():

    import os

    client = redis.Redis(
      host=os.getenv("REDIS_HOST", "localhost"),
      port=int(os.getenv("REDIS_PORT", 6379)),
      password=os.getenv("REDIS_PASSWORD", "redis123"),
      decode_responses=True,
    )

    queue = IngestionQueue(client)

    await queue.enqueue(
        "doc1",
        "/tmp/file.pdf",
        "pdf",
    )

    job = await queue.dequeue()

    assert job["document_id"] == "doc1"
    assert job["source_type"] == "pdf"

    await client.aclose()