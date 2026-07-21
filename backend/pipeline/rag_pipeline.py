from typing import Any
import time
from uuid import UUID

from backend.retrieval.retriever import Retriever
from backend.retrieval.context_assembler import ContextAssembler
from backend.generation.generator import Generator


class RAGPipeline:
    """
    End-to-End Retrieval Augmented Generation Pipeline.

    Flow:
    User Query
        ↓
    Retriever
        ↓
    Context Assembler
        ↓
    Generator
        ↓
    Response
    """

    def __init__(
        self,
        retriever=None,
        generator=None,
        context_assembler=None,
    ):

        self.retriever = retriever or Retriever()

        if generator is None:
            raise ValueError(
                "Generator instance required"
            )

        self.generator = generator

        self.context_assembler = (
            context_assembler
            or ContextAssembler()
        )

    async def run(
        self,
        query: str,
        pipeline_id: UUID,
        stream: bool = False,
        top_k: int = 5,
    ) -> dict[str, Any] | Any:
        """
        Execute complete RAG pipeline.
        """

        start_time = time.perf_counter()

        # --------------------------------------------------
        # Retrieval
        # --------------------------------------------------

        chunks = await self.retriever.hybrid_retrieve(
            query=query,
            k=top_k,
        )

        # --------------------------------------------------
        # Context Assembly
        # --------------------------------------------------

        assembled = self.context_assembler.assemble(
            chunks
        )

        context = assembled.get(
            "context",
            "",
        )

        sources = assembled.get(
            "sources",
            [],
        )

        # --------------------------------------------------
        # Query Classification
        # --------------------------------------------------

        query_type = "factual"

        if hasattr(
            self.retriever,
            "query_processor",
        ):

            processed = await (
                self.retriever
                .query_processor
                .process(query)
            )

            query_type = processed.get(
                "query_type",
                "factual",
            )

        # --------------------------------------------------
        # Streaming
        # --------------------------------------------------

        if stream:

            return self.generator.stream_generate(
                question=query,
                context=context,
                sources=sources,
                pipeline_id=pipeline_id,
                query_type=query_type,
            )

        # --------------------------------------------------
        # Generation
        # --------------------------------------------------

        generation = await self.generator.generate(
            question=query,
            context=context,
            sources=sources,
            pipeline_id=pipeline_id,
            query_type=query_type,
        )

        latency = (
            time.perf_counter()
            - start_time
        ) * 1000

        return {

            "run_id": generation["run_id"],

            "query": query,

            "query_type": query_type,

            "answer": generation["answer"],

            "citations": generation["citations"],

            "context": context,

            "context_metadata": {

                "chunks_used": len(
                    assembled.get(
                        "chunks_used",
                        [],
                    )
                ),

                "total_tokens": assembled.get(
                    "total_tokens",
                    0,
                ),

                "sources": sources,
            },

            "retrieved_chunks": len(
                chunks
            ),

            "latency_ms": round(
                latency,
                2,
            ),
        }