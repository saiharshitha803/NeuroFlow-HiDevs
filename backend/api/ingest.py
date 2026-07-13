from uuid import uuid4
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter()


@router.post("/ingest")
async def ingest(
    file: UploadFile = File(...),
):
    """
    Queue a document for ingestion.
    """

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".csv",
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
    }

    filename = file.filename

    if filename is None:
        raise HTTPException(
            status_code=400,
            detail="Missing filename",
        )

    

    extension = Path(filename).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type",
        )

    document_id = str(uuid4())

    return {
        "document_id": document_id,
        "status": "queued",
        "duplicate": False,
    }


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
):
    """
    Temporary document status endpoint.
    """

    return {
        "document_id": document_id,
        "status": "queued",
        "chunk_count": 0,
        "metadata": {},
    }