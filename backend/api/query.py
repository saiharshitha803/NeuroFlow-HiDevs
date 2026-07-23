from uuid import UUID
import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
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

from backend.repositories.evaluation_repository import (
    EvaluationRepository,
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
# Model Router
# --------------------------------------------------

model_router = ModelRouter(
    redis_client=redis_client,
)

# --------------------------------------------------
# LLM Client
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

# --------------------------------------------------
# Generator
# --------------------------------------------------

generator = Generator(
    client=llm_client,
)

rag_pipeline = RAGPipeline(
    generator=generator,
)

pipeline_repo = PipelineRepository()

evaluation_repo = EvaluationRepository()

# ==================================================
# Request Models
# ==================================================


class QueryRequest(BaseModel):
    query: str
    pipeline_id: UUID
    stream: bool = False


class RatingRequest(BaseModel):
    rating: int


# ==================================================
# Query Endpoint
# ==================================================

@router.post("/query")
async def query(request: QueryRequest):

    pipeline = await pipeline_repo.get_pipeline(
        request.pipeline_id
    )

    if pipeline is None:
        raise HTTPException(
            status_code=404,
            detail="Pipeline not found",
        )

    if request.stream:

        async def event_generator():

            async for event in rag_pipeline.run(
                query=request.query,
                pipeline_id=request.pipeline_id,
                stream=True,
            ):

                yield event

        return EventSourceResponse(
            event_generator()
        )

    result = await rag_pipeline.run(
        query=request.query,
        pipeline_id=request.pipeline_id,
        stream=False,
    )

    return JSONResponse(result)


# ==================================================
# User Rating Endpoint
# ==================================================

@router.patch("/runs/{run_id}/rating")
async def rate_run(
    run_id: UUID,
    request: RatingRequest,
):

    if request.rating < 1 or request.rating > 5:

        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5",
        )

    await evaluation_repo.update_user_rating(
        run_id,
        request.rating,
    )

    evaluation = await evaluation_repo.get_evaluation(
        run_id,
    )

    if evaluation is None:

        raise HTTPException(
            status_code=404,
            detail="Evaluation not found",
        )

    automated = evaluation["overall_score"]

    human = request.rating / 5

    calibration_needed = (
        abs(
            automated - human
        ) > 0.3
    )

    metadata = {
        "calibration_needed": calibration_needed
    }

    await evaluation_repo.update_metadata(
        run_id,
        metadata,
    )

    return {
        "message": "Rating stored successfully",
        "calibration_needed": calibration_needed,
    }