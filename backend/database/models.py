from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID


@dataclass
class Document:
    """
    Represents a document stored in database.
    """

    id: UUID

    filename: str

    created_at: Optional[str] = None



@dataclass
class Chunk:
    """
    Represents a document chunk.

    Matches chunks table.
    """

    id: UUID

    document_id: UUID

    content: str

    chunk_index: int

    token_count: int

    embedding: Optional[list[float]] = None

    metadata: dict[str, Any] | None = None



@dataclass
class Evaluation:
    """
    Represents retrieval/generation evaluation results.
    """

    id: UUID

    pipeline_id: UUID

    score: float

    metrics: dict[str, Any] | None = None



@dataclass
class Pipeline:
    """
    Represents RAG pipeline configuration.
    """

    id: UUID

    name: str

    config: dict[str, Any] | None = None



@dataclass
class PipelineRun:
    """
    Represents a pipeline execution.
    """

    id: UUID

    pipeline_id: UUID

    status: str

    metadata: dict[str, Any] | None = None