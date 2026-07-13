from pipelines.ingestion.chunker import Chunker
from pipelines.ingestion.models import ExtractedPage


def test_hierarchical_chunker():

    pages = [

        ExtractedPage(
            page_number=1,
            content="Introduction",
            content_type="text",
            metadata={
                "level": "h1",
            },
        ),

        ExtractedPage(
            page_number=2,
            content="This is section one.",
            content_type="text",
            metadata={
                "level": "h2",
            },
        ),

    ]

    chunker = Chunker()

    chunks = chunker.chunk(
        pages,
        strategy="hierarchical",
    )

    assert len(chunks) == 2

    assert chunks[1].metadata["parent"] == chunks[0].chunk_id