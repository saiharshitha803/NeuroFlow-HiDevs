import hashlib

from backend.database.document_repository import DocumentRepository
from backend.database.chunk_repository import ChunkRepository
from backend.embeddings.provider import EmbeddingProvider
from backend.database.connection import db


class SimpleIngestor:
    """
    Minimal ingestion pipeline for retrieval evaluation.
    """

    def __init__(self):

        self.documents = DocumentRepository()

        self.chunks = ChunkRepository()

        self.embedding = EmbeddingProvider()



    async def ingest(
        self,
        filename: str,
        content: str,
    ):

        content_hash = hashlib.sha256(
            content.encode()
        ).hexdigest()



        document = await self.documents.find_duplicate(
            content_hash
        )


        if document:
            return document["id"]



        document_id = await self.documents.create(
            filename=filename,
            source_type="text",
            content_hash=content_hash,
        )



        # simple chunking
        chunk_size = 80

        words = content.split()



        chunks = [
            " ".join(
                words[i:i + chunk_size]
            )

            for i in range(
                0,
                len(words),
                chunk_size
            )
        ]



        for index, chunk_text in enumerate(chunks):


            chunk_id = await self.chunks.create(
                document_id=document_id,
                chunk_index=index,
                content=chunk_text,
                metadata={
                    "filename": filename,
                    "page": index + 1
                }
            )


            vector = await self.embedding.embed(
                chunk_text
            )


            from backend.retrieval.vector_repository import VectorRepository


            vector_repo = VectorRepository()


            await vector_repo.upsert_embedding(
                chunk_id,
                vector
            )



        await self.documents.update_status(
            document_id,
            "completed"
        )


        return document_id