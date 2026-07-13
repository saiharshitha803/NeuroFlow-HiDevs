from pipelines.ingestion.models import (
    ExtractedPage,
    Chunk,
)


def test_extracted_page():

    page = ExtractedPage(
        page_number=1,
        content="Hello",
        content_type="text",
    )

    assert page.page_number == 1
    assert page.content == "Hello"
    assert page.content_type == "text"
    assert page.metadata == {}


def test_chunk():

    chunk = Chunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        chunk_index=0,
        text="Sample text",
    )

    assert chunk.chunk_id == "chunk-1"
    assert chunk.document_id == "doc-1"
    assert chunk.chunk_index == 0
    assert chunk.text == "Sample text"