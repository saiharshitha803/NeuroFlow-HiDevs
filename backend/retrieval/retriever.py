from backend.retrieval.vector_repository import VectorRepository
from backend.embeddings.provider import EmbeddingProvider


class Retriever:
    """
    Retrieves the most relevant chunks for a user query or embedding.
    """

    def __init__(self):
        self.vector_repository = VectorRepository()
        self.embedding_provider = EmbeddingProvider()

    async def retrieve(
        self,
        query,
        top_k: int = 5,
    ):
        # If already an embedding, use it directly
        if isinstance(query, list):
            embedding = query
        else:
            embedding = await self.embedding_provider.embed(query)

        return await self.vector_repository.similarity_search(
            embedding=embedding,
            limit=top_k,
        )