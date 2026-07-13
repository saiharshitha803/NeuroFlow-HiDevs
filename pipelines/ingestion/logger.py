import json
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("ingestion")


def log_ingestion_complete(
    document_id: str,
    duration_ms: float,
    chunks: int,
    tokens: int,
):
    logger.info(
        json.dumps(
            {
                "event": "ingestion_complete",
                "document_id": document_id,
                "duration_ms": duration_ms,
                "chunks": chunks,
                "tokens": tokens,
            }
        )
    )