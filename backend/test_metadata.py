import asyncio

from backend.database.connection import db
from backend.pipeline.rag_pipeline import RAGPipeline


async def main():

    print("Starting metadata retrieval test...\n")


    # Start database connection
    await db.connect()


    pipeline = RAGPipeline()


    query = (
        "Show me documents from 2023 about climate change"
    )


    print("Query:")
    print(query)
    print()


    result = await pipeline.run(
        query
    )


    print("====================")
    print("METADATA TEST RESULT")
    print("====================")


    print(result)


    # Close database
    await db.disconnect()



if __name__ == "__main__":

    asyncio.run(main())