import json

import redis.asyncio as redis


QUEUE_NAME = "queue:ingest"


class IngestionQueue:

    def __init__(
        self,
        redis_client: redis.Redis,
    ):
        self.redis = redis_client

    async def enqueue(
        self,
        document_id: str,
        file_path: str,
        source_type: str,
    ) -> None:
        """
        Add a new ingestion job.
        """

        payload = {
            "document_id": document_id,
            "file_path": file_path,
            "source_type": source_type,
        }

        await self.redis.lpush(
            QUEUE_NAME,
            json.dumps(payload),
        )

    async def dequeue(
        self,
        timeout: int = 5,
    ) -> dict | None:
        """
        Wait for the next job.
        """

        result = await self.redis.brpop(
            QUEUE_NAME,
            timeout=timeout,
        )

        if result is None:
            return None

        _, payload = result

        return json.loads(payload)

    async def size(
        self,
    ) -> int:
        """
        Current queue size.
        """

        return await self.redis.llen(
            QUEUE_NAME
        )
    

async def dequeue(
    self,
    timeout: int = 5,
):

    result = await self.redis.brpop(
        QUEUE_NAME,
        timeout=timeout,
    )

    if result is None:
        return None

    _, payload = result

    if isinstance(payload, bytes):
        payload = payload.decode()

    return json.loads(payload)