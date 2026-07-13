from pipelines.ingestion.chunker import Chunker
from pipelines.ingestion.models import ExtractedPage


def test_semantic_chunker():

    page = ExtractedPage(
        page_number=1,
        content=(
            "Artificial Intelligence is changing the world. "
            "Machine learning enables prediction. "
            "Deep learning uses neural networks. "
            "Cats are wonderful pets. "
            "Dogs are loyal animals."
        ),
        content_type="text",
        metadata={},
    )

    chunker = Chunker()

    chunks = chunker.chunk(
        [page],
        strategy="semantic",
    )

    assert len(chunks) >= 1