import pytest

from pipelines.ingestion.worker import IngestionWorker


class MockQueue:

    async def dequeue(self):
        return {
            "document_id": "doc123",
            "file_path": "sample.pdf",
            "source_type": "pdf",
        }


class MockExtractor:

    async def __call__(self, file_path):
        return [
            type(
                "Page",
                (),
                {
                    "page_number": 1,
                    "content": "Hello World",
                    "content_type": "text",
                    "metadata": {},
                },
            )()
        ]


class MockChunk:

    def __init__(self, text):
        self.text = text


class MockChunker:

    def chunk(self, pages, document_id):
        return [
            MockChunk("Chunk 1"),
            MockChunk("Chunk 2"),
        ]


@pytest.mark.asyncio
async def test_worker_process_once():

    worker = IngestionWorker(
        queue=MockQueue(),
        extractors={
            "pdf": MockExtractor(),
        },
    )

    worker.chunker = MockChunker()

    result = await worker.process_once()

    assert result["document_id"] == "doc123"
    assert result["pages"] == 1
    assert result["chunks"] == 2