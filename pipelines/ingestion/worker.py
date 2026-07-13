import time
from typing import Callable

from pipelines.ingestion.chunker import Chunker
from pipelines.ingestion.logger import log_ingestion_complete
from pipelines.ingestion.queue import IngestionQueue
from pipelines.ingestion.telemetry import IngestionTelemetry


class IngestionWorker:
    """
    Background worker that continuously processes
    ingestion jobs from Redis.
    """

    def __init__(
        self,
        queue: IngestionQueue,
        extractors: dict[str, Callable],
    ):
        self.queue = queue
        self.extractors = extractors
        self.chunker = Chunker()
        self.telemetry = IngestionTelemetry()

    async def process_once(self):
        """
        Process a single ingestion job.
        """

        job = await self.queue.dequeue()

        if job is None:
            return None

        document_id = job["document_id"]
        source_type = job["source_type"]

        extractor = self.extractors.get(source_type)

        if extractor is None:
            raise ValueError(
                f"No extractor registered for '{source_type}'"
            )

        start = time.perf_counter()

        with self.telemetry.start_span() as span:

            pages = await extractor(
                job["file_path"]
            )

            chunks = self.chunker.chunk(
                pages,
                document_id=document_id,
            )

            duration_ms = (
                time.perf_counter() - start
            ) * 1000

            token_count = sum(
                len(chunk.text.split())
                for chunk in chunks
            )

            self.telemetry.add_attributes(
                span,
                document_id=document_id,
                source_type=source_type,
                page_count=len(pages),
                chunk_count=len(chunks),
                embedding_calls=0,
            )

        log_ingestion_complete(
            document_id=document_id,
            duration_ms=duration_ms,
            chunks=len(chunks),
            tokens=token_count,
        )

        return {
            "document_id": document_id,
            "pages": len(pages),
            "chunks": len(chunks),
            "duration_ms": duration_ms,
        }

    async def run(self):
        """
        Continuously process jobs from the queue.
        """

        while True:
            await self.process_once()