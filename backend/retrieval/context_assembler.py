import json
import tiktoken


class ContextAssembler:
    """
    Builds final LLM context from retrieved chunks.
    """

    def __init__(
        self,
        token_budget: int = 4000
    ):

        self.token_budget = token_budget

        self.encoder = tiktoken.get_encoding(
            "cl100k_base"
        )


    def count_tokens(
        self,
        text: str
    ) -> int:

        return len(
            self.encoder.encode(text)
        )


    def _get_metadata(
        self,
        chunk
    ):

        metadata = getattr(
            chunk,
            "metadata",
            {}
        )


        # Handle JSON string from postgres
        if isinstance(
            metadata,
            str
        ):

            try:

                metadata = json.loads(
                    metadata
                )

            except Exception:

                metadata = {}


        if metadata is None:

            metadata = {}


        return metadata



    def assemble(
        self,
        chunks
    ):

        context_parts = []

        used_chunks = []

        sources = []

        total_tokens = 0



        for index, chunk in enumerate(
            chunks,
            start=1
        ):


            metadata = self._get_metadata(
                chunk
            )


            document_name = metadata.get(
                "filename",
                "unknown"
            )


            page = metadata.get(
                "page",
                "unknown"
            )


            formatted = (
                f"[Source {index} — "
                f"{document_name}, "
                f"page {page}]\n\n"
                f"{chunk.content}"
            )


            tokens = self.count_tokens(
                formatted
            )


            if (
                total_tokens + tokens
                >
                self.token_budget
            ):
                break



            context_parts.append(
                formatted
            )


            used_chunks.append(
                chunk
            )


            sources.append(
                {
                    "document": document_name,
                    "page": page,
                    "chunk_id": chunk.chunk_id
                }
            )


            total_tokens += tokens



        return {

            "context":
                "\n\n".join(
                    context_parts
                ),

            "chunks_used":
                used_chunks,

            "total_tokens":
                total_tokens,

            "sources":
                sources
        }