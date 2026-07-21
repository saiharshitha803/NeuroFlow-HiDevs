from uuid import UUID
import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

import redis.asyncio as redis

from backend.config import settings

from backend.pipeline.rag_pipeline import RAGPipeline
from backend.generation.generator import Generator

from backend.providers.client import NeuroFlowClient
from backend.providers.router import ModelRouter
from backend.providers.openai_provider import OpenAIProvider

from backend.repositories.pipeline_repository import (
    PipelineRepository,
)


router = APIRouter(
    prefix="/api",
    tags=["Query"],
)


# --------------------------------------------------
# Redis
# --------------------------------------------------

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
)


# --------------------------------------------------
# Router
# --------------------------------------------------

model_router = ModelRouter(
    redis_client=redis_client,
)


# --------------------------------------------------
# Client
# --------------------------------------------------

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


generator = Generator(
    client=llm_client,
)

rag_pipeline = RAGPipeline(
    generator=generator,
)

pipeline_repo = PipelineRepository()


# --------------------------------------------------
# Request
# --------------------------------------------------

class QueryRequest(BaseModel):

    query: str = Field(
        ...,
        min_length=3,
    )

    pipeline_id: UUID | None = None

    stream: bool = False


# --------------------------------------------------
# POST /query
# --------------------------------------------------

@router.post("/query")
async def query(
    request: QueryRequest,
):

    try:

        pipeline_id = request.pipeline_id

        if pipeline_id is None:

            pipeline = await pipeline_repo.get_pipeline_by_name(
                "default"
            )

            if pipeline is None:

                pipeline_id = await pipeline_repo.create_pipeline(
                    name="default",
                    config={},
                )

            else:

                pipeline_id = pipeline["id"]

        if request.stream:

            return JSONResponse(
                {
                    "run_id": "pending",
                    "message":
                        "Connect to "
                        "/api/query/pending/stream",
                }
            )

        result = await rag_pipeline.run(
            query=request.query,
            pipeline_id=pipeline_id,
            stream=False,
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# --------------------------------------------------
# GET /query/{run_id}/stream
# --------------------------------------------------

@router.get(
    "/query/{run_id}/stream"
)
async def stream_query(
    run_id: str,
):

    async def event_generator():

        yield {
            "event": "message",
            "data": '{"type":"retrieval_start"}',
        }

        await asyncio.sleep(1)

        yield {
            "event": "message",
            "data": '{"type":"retrieval_complete"}',
        }

        demo_tokens = [
            "Based",
            " on",
            " the",
            " retrieved",
            " documents,",
            " HNSW",
            " indexing",
            " builds",
            " a",
            " graph",
            " for",
            " approximate",
            " nearest",
            " neighbor",
            " search.",
        ]

        for token in demo_tokens:

            yield {
                "event": "message",
                "data": (
                    f'{{"type":"token","delta":"{token}"}}'
                ),
            }

            await asyncio.sleep(0.15)

        yield {
            "event": "message",
            "data": '{"type":"done"}',
        }

    return EventSourceResponse(
        event_generator()
    )


print("QUERY ROUTER LOADED")
print(router.routes)