from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtractedPage:
    """
    Represents a single extracted unit from a document.

    A PDF page, DOCX section, CSV block, image description,
    or webpage content is converted into one or more
    ExtractedPage objects.
    """

    page_number: int

    content: str

    content_type: str
    # text | table | image_description

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Chunk:
    """
    Represents a chunk ready for embedding.
    """

    chunk_id: str

    document_id: str

    chunk_index: int

    text: str

    metadata: dict[str, Any] = field(default_factory=dict)