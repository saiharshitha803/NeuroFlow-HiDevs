import asyncio
from typing import Any

from backend.retrieval.vector_repository import VectorRepository
from backend.database.chunk_repository import ChunkRepository
from backend.embeddings.provider import EmbeddingProvider

from backend.retrieval.query_processor import QueryProcessor
from backend.retrieval.fusion import reciprocal_rank_fusion
from backend.retrieval.reranker import CrossEncoderReranker



class RetrievalResult:
    """
    Standard retrieval object used by:
    Dense retrieval
    Sparse retrieval
    Metadata retrieval
    RRF
    Reranker
    """

    def __init__(
        self,
        data: dict[str, Any]
    ):

        self.data = data

        self.chunk_id = str(
            data["id"]
        )

        self.content = data.get(
            "content",
            ""
        )

        self.metadata = data.get(
            "metadata",
            {}
        )

        self.score = 0



    def __getattr__(
        self,
        key
    ):

        return self.data.get(key)



class Retriever:
    """
    Production Retrieval Pipeline

    Query Processing
          |
          |
    +-------------+
    |             |
 Dense        Sparse
    |             |
    +-------------+
          |
     Metadata
          |
          ↓
        RRF Fusion
          |
          ↓
   Cross Encoder Reranking
          |
          ↓
      Final Results
    """



    def __init__(self):

        self.vector_repository = VectorRepository()

        self.chunk_repository = ChunkRepository()

        self.embedding_provider = EmbeddingProvider()

        self.query_processor = QueryProcessor()

        self.reranker = CrossEncoderReranker()



    async def retrieve(
        self,
        query,
        top_k: int = 5
    ):
        """
        Main retrieval entry point.

        Evaluation and APIs call this method.

        Uses complete hybrid pipeline.
        """

        return await self.hybrid_retrieve(
            query=query,
            k=top_k
        )



    async def hybrid_retrieve(
        self,
        query: str,
        k: int = 10
    ):

        # -----------------------------
        # Step 1
        # Query Processing
        # -----------------------------

        processed = await self.query_processor.process(
            query
        )


        expanded_queries = processed.get(
            "expanded_queries",
            [query]
        )


        filters = processed.get(
            "filters",
            {}
        )



        # -----------------------------
        # Step 2
        # Parallel Retrieval
        # -----------------------------

        dense_results, sparse_results, metadata_results = await asyncio.gather(

            self._dense_retrieval(
                expanded_queries,
                k
            ),

            self._sparse_retrieval(
                query,
                k
            ),

            self._metadata_retrieval(
                filters,
                k
            )

        )



        # -----------------------------
        # Step 3
        # Reciprocal Rank Fusion
        # -----------------------------

        fused_results = reciprocal_rank_fusion(
            [
                dense_results,
                sparse_results,
                metadata_results
            ]
        )



        # -----------------------------
        # Step 4
        # Cross Encoder Reranking
        # -----------------------------

        reranked = await self.reranker.rerank(
            query=query,
            candidates=fused_results[:40],
            top_k=k
        )


        return reranked



    async def _dense_retrieval(
        self,
        queries,
        k
    ):

        all_results = []


        for query in queries:

            embedding = await self.embedding_provider.embed(
                query
            )


            chunks = await self.vector_repository.similarity_search(
                embedding=embedding,
                limit=k
            )


            all_results.extend(
                self._normalize(chunks)
            )


        return all_results



    async def _sparse_retrieval(
        self,
        query,
        k
    ):

        results = await self.chunk_repository.full_text_search(
            query=query,
            limit=k
        )


        return self._normalize(
            results
        )



    async def _metadata_retrieval(
        self,
        filters,
        k
    ):

        if not filters:

            return []


        results = await self.chunk_repository.metadata_search(
            filters=filters,
            limit=k
        )


        return self._normalize(
            results
        )



    def _normalize(
        self,
        results
    ):

        return [

            RetrievalResult(
                dict(item)
            )

            for item in results

        ]