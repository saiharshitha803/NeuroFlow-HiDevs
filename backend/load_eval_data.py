import asyncio

from backend.database.connection import db
from backend.pipelines.ingestion.simple_ingest import SimpleIngestor



DATA = [

(
"hnsw.txt",
"""
HNSW stands for Hierarchical Navigable Small World.
It is an approximate nearest neighbor search algorithm.
HNSW builds a graph structure for fast vector similarity search.
It is commonly used with vector databases and pgvector indexing.
"""
),


(
"transformers.txt",
"""
Transformers are neural network architectures based on attention.
Self attention allows models to understand relationships between tokens.
Attention weights determine the importance of different tokens.
"""
),


(
"embeddings.txt",
"""
Vector embeddings represent text as numerical vectors.
Similar meanings produce similar vectors in embedding space.
Embedding models are used in semantic search and retrieval augmented generation.
"""
)

]



async def main():

    await db.connect()


    ingestor = SimpleIngestor()


    for filename, content in DATA:

        doc_id = await ingestor.ingest(
            filename,
            content
        )

        print(
            "Inserted:",
            filename,
            doc_id
        )


    await db.disconnect()



asyncio.run(main())