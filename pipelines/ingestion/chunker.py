import re

import tiktoken

from pipelines.ingestion.models import (
    Chunk,
    ExtractedPage,
)


class Chunker:
    """
    NeuroFlow Chunker

    Supports:
    - Fixed-size chunking
    - Hierarchical chunking
    - Semantic chunking
    - Automatic strategy selection
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
    ):

        self.encoding = tiktoken.encoding_for_model(model)

        self.chunk_size = 512
        self.overlap = 64

    def _token_count(
        self,
        text: str,
    ) -> int:

        return len(
            self.encoding.encode(text)
        )

    ####################################################################
    # Fixed Size Chunking
    ####################################################################

    def _fixed_size(
        self,
        pages: list[ExtractedPage],
        document_id: str = "",
    ) -> list[Chunk]:

        chunks: list[Chunk] = []

        chunk_index = 0

        for page in pages:

            tokens = self.encoding.encode(
                page.content
            )

            start = 0

            while start < len(tokens):

                end = min(
                    start + self.chunk_size,
                    len(tokens),
                )

                chunk_text = self.encoding.decode(
                    tokens[start:end]
                )

                chunks.append(

                    Chunk(

                        chunk_id=f"chunk_{chunk_index}",

                        document_id=document_id,

                        chunk_index=chunk_index,

                        text=chunk_text,

                        metadata={

                            **page.metadata,

                            "page_number": page.page_number,

                            "content_type": page.content_type,

                            "strategy": "fixed_size",

                            "token_count": len(
                                tokens[start:end]
                            ),

                        },

                    )

                )

                chunk_index += 1

                start += (
                    self.chunk_size
                    - self.overlap
                )

        return chunks

    ####################################################################
    # Hierarchical Chunking
    ####################################################################

    def _hierarchical(
        self,
        pages: list[ExtractedPage],
        document_id: str = "",
    ) -> list[Chunk]:

        chunks: list[Chunk] = []

        chunk_index = 0

        current_parent = None

        for page in pages:

            level = page.metadata.get("level")

            chunk_id = f"chunk_{chunk_index}"

            if level == "h1":

                current_parent = chunk_id

            metadata = {

                **page.metadata,

                "page_number": page.page_number,

                "content_type": page.content_type,

                "strategy": "hierarchical",

                "parent": current_parent,

            }

            chunks.append(

                Chunk(

                    chunk_id=chunk_id,

                    document_id=document_id,

                    chunk_index=chunk_index,

                    text=page.content,

                    metadata=metadata,

                )

            )

            chunk_index += 1

        return chunks

    ####################################################################
    # Semantic Chunking
    ####################################################################

    def _semantic(
        self,
        pages: list[ExtractedPage],
        document_id: str = "",
    ) -> list[Chunk]:

        chunks: list[Chunk] = []

        chunk_index = 0

        for page in pages:

            sentences = re.split(
                r"(?<=[.!?])\s+",
                page.content.strip(),
            )

            current_chunk = ""

            current_tokens = 0

            for sentence in sentences:

                if not sentence.strip():
                    continue

                sentence_tokens = len(
                    self.encoding.encode(sentence)
                )

                if (

                    current_tokens
                    + sentence_tokens

                    > self.chunk_size

                    and current_chunk

                ):

                    chunks.append(

                        Chunk(

                            chunk_id=f"chunk_{chunk_index}",

                            document_id=document_id,

                            chunk_index=chunk_index,

                            text=current_chunk.strip(),

                            metadata={

                                **page.metadata,

                                "page_number": page.page_number,

                                "content_type": page.content_type,

                                "strategy": "semantic",

                            },

                        )

                    )

                    chunk_index += 1

                    current_chunk = sentence

                    current_tokens = sentence_tokens

                else:

                    if current_chunk:

                        current_chunk += " "

                    current_chunk += sentence

                    current_tokens += sentence_tokens

            if current_chunk:

                chunks.append(

                    Chunk(

                        chunk_id=f"chunk_{chunk_index}",

                        document_id=document_id,

                        chunk_index=chunk_index,

                        text=current_chunk.strip(),

                        metadata={

                            **page.metadata,

                            "page_number": page.page_number,

                            "content_type": page.content_type,

                            "strategy": "semantic",

                        },

                    )

                )

                chunk_index += 1

        return chunks

    ####################################################################
    # Public API
    ####################################################################

    def chunk(
        self,
        pages: list[ExtractedPage],
        document_id: str = "",
        strategy: str | None = None,
    ) -> list[Chunk]:
        """
        Automatically select the best chunking strategy.

        Rules:
        - Tables -> Fixed Size
        - Documents with headings -> Hierarchical
        - PDFs with >50 pages -> Semantic
        - Otherwise -> Fixed Size
        """

        if not pages:
            return []

        ################################################################
        # Manual Override
        ################################################################

        if strategy is not None:

            if strategy == "fixed_size":

                return self._fixed_size(
                    pages,
                    document_id,
                )

            if strategy == "hierarchical":

                return self._hierarchical(
                    pages,
                    document_id,
                )

            if strategy == "semantic":

                return self._semantic(
                    pages,
                    document_id,
                )

            raise ValueError(
                f"Unknown strategy: {strategy}"
            )

        ################################################################
        # Automatic Strategy Selection
        ################################################################

        first_page = pages[0]

        # Tables
        if first_page.content_type == "table":

            return self._fixed_size(
                pages,
                document_id,
            )

        # DOCX Headings
        if any(

            page.metadata.get("level")

            for page in pages

        ):

            return self._hierarchical(
                pages,
                document_id,
            )

        # Large PDFs
        if len(pages) > 50:

            return self._semantic(
                pages,
                document_id,
            )

        # Default

        return self._fixed_size(
            pages,
            document_id,
        )