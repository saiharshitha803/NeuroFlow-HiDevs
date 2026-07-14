from typing import Any
import time

from backend.retrieval.retriever import Retriever
from backend.retrieval.context_assembler import ContextAssembler
from backend.generation.generator import Generator


class RAGPipeline:
    """
    End-to-End Retrieval Augmented Generation pipeline.

    Flow:

    User Query
        |
        ↓
    Hybrid Retrieval
        |
        ↓
    RRF Fusion
        |
        ↓
    Cross Encoder Reranking
        |
        ↓
    Context Assembly
        |
        ↓
    Generator
        |
        ↓
    Final Answer
    """

    def __init__(
        self,
        retriever=None,
        generator=None,
        context_assembler=None,
    ):

        self.retriever = (
            retriever
            or Retriever()
        )

        self.generator = (
            generator
            or Generator()
        )

        self.context_assembler = (
            context_assembler
            or ContextAssembler()
        )


    async def run(
        self,
        query: str,
        top_k: int = 5,
    ) -> dict[str, Any]:

        start_time = time.perf_counter()


        # -----------------------------
        # 1. Retrieve relevant chunks
        # -----------------------------

        chunks = await self.retriever.hybrid_retrieve(
            query=query,
            k=top_k,
        )


        # -----------------------------
        # 2. Assemble context
        # -----------------------------

        assembled = self.context_assembler.assemble(
            chunks
        )


        context = assembled["context"]

        sources = assembled["sources"]

        used_chunks = assembled["chunks_used"]

        total_tokens = assembled["total_tokens"]



        # -----------------------------
        # 3. Generate answer
        # -----------------------------

        answer = await self.generator.generate(
            question=query,
            context=context,
        )


        latency = (
            time.perf_counter()
            -
            start_time
        ) * 1000



        # -----------------------------
        # 4. Final response
        # -----------------------------

        return {

            "query": query,

            "answer": answer,

            "context": context,

            "context_metadata": {

                "chunks_used": len(
                    used_chunks
                ),

                "total_tokens": total_tokens,

                "sources": sources,

            },

            "retrieved_chunks": len(chunks),

            "latency_ms": round(
                latency,
                2
            ),

        }