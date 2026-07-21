import asyncio
import json

import redis.asyncio as redis

from backend.config import settings

from backend.database.connection import db

from backend.pipeline.rag_pipeline import RAGPipeline

from backend.generation.generator import Generator

from backend.providers.client import NeuroFlowClient
from backend.providers.router import ModelRouter
from backend.providers.openai_provider import OpenAIProvider



async def main():

    print("\nStarting RAG test...\n")


    # -----------------------------
    # Database connection
    # -----------------------------

    await db.connect()



    # -----------------------------
    # Redis
    # -----------------------------

    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
    )



    # -----------------------------
    # Router
    # -----------------------------

    model_router = ModelRouter(
        redis_client=redis_client
    )



    # -----------------------------
    # LLM Client
    # -----------------------------

    llm_client = NeuroFlowClient(
        router=model_router,
        redis_client=redis_client,
    )


    llm_client.register_provider(
        "openai",
        OpenAIProvider(
            api_key=settings.OPENROUTER_API_KEY,
            model=settings.GENERATION_MODEL,
        ),
    )



    # -----------------------------
    # Generator
    # -----------------------------

    generator = Generator(
        client=llm_client
    )



    # -----------------------------
    # RAG Pipeline
    # -----------------------------

    pipeline = RAGPipeline(
        generator=generator
    )



    try:

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

        await db.disconnect()

        await redis_client.aclose()



if __name__ == "__main__":

    asyncio.run(main())