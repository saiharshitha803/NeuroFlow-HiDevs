from pipelines.ingestion.chunker import Chunker
from pipelines.ingestion.models import ExtractedPage


def test_chunker():

    page = ExtractedPage(
        page_number=1,
        content="Hello " * 1000,
        content_type="text",
        metadata={},
    )

    chunker = Chunker()

    chunks = chunker.chunk([page])

    assert len(chunks) > 1