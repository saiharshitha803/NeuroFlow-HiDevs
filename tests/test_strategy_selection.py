from pipelines.ingestion.chunker import Chunker
from pipelines.ingestion.models import ExtractedPage


def test_auto_strategy():

    pages = [

        ExtractedPage(
            page_number=1,
            content="Heading",
            content_type="text",
            metadata={
                "level": "h1",
            },
        ),

        ExtractedPage(
            page_number=2,
            content="Paragraph",
            content_type="text",
            metadata={
                "level": "h2",
            },
        ),

    ]

    chunker = Chunker()

    chunks = chunker.chunk(
        pages
    )

    assert chunks[0].metadata["strategy"] == "hierarchical"