import asyncio
import json

from backend.database.connection import db
from backend.pipeline.rag_pipeline import RAGPipeline


async def main():

    print("\nStarting RAG test...\n")

    # Connect database
    await db.connect()

    try:

        pipeline = RAGPipeline()


        query = "What is HNSW indexing?"


        print("Query:")
        print(query)


        result = await pipeline.run(
            query
        )


        print("\n====================")
        print("RAG RESPONSE")
        print("====================")


        print(
            json.dumps(
                result,
                indent=4,
                default=str
            )
        )


    finally:

        # Close database
        await db.disconnect()



if __name__ == "__main__":

    asyncio.run(main())