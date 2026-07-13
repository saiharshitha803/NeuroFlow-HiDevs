from backend.pipelines.ingestion.telemetry import IngestionTelemetry


def test_telemetry_attributes():

    telemetry = IngestionTelemetry()

    with telemetry.start_span() as span:

        telemetry.add_attributes(
            span,
            document_id="doc-123",
            source_type="pdf",
            page_count=5,
            chunk_count=20,
            embedding_calls=3,
        )

    assert span.attributes["document_id"] == "doc-123"
    assert span.attributes["source_type"] == "pdf"
    assert span.attributes["page_count"] == 5
    assert span.attributes["chunk_count"] == 20
    assert span.attributes["embedding_calls"] == 3