from backend.pipelines.ingestion.logger import log_ingestion_complete


def test_logger_runs():
    log_ingestion_complete(
        document_id="doc-1",
        duration_ms=123.4,
        chunks=10,
        tokens=500,
    )