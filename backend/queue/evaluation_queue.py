import json

import redis.asyncio as redis

from backend.config import settings

from backend.providers.client import NeuroFlowClient
from backend.providers.router import ModelRouter
from backend.providers.openai_provider import OpenAIProvider

from backend.evaluation.judge import EvaluationJudge
from backend.repositories.training_pair_repository import (
    TrainingPairRepository,
)

from backend.repositories.pipeline_run_repository import (
    PipelineRunRepository,
)


# ---------------------------------------
# Redis
# ---------------------------------------

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
)


# ---------------------------------------
# Model Router
# ---------------------------------------

model_router = ModelRouter(
    redis_client=redis_client,
)


# ---------------------------------------
# LLM Client
# ---------------------------------------

client = NeuroFlowClient(
    router=model_router,
    redis_client=redis_client,
)

client.register_provider(
    "openai",
    OpenAIProvider(
        api_key=settings.OPENROUTER_API_KEY,
        model=settings.GENERATION_MODEL,
    ),
)


# ---------------------------------------
# Judge & Repository
# ---------------------------------------

judge = EvaluationJudge(client)

pipeline_runs = PipelineRunRepository()

training_pairs = TrainingPairRepository()

# ---------------------------------------
# Producer
# ---------------------------------------

async def enqueue_evaluation(run_id):
    """
    Push a completed run onto the Redis evaluation queue.
    """

    await redis_client.lpush(
        "evaluation_jobs",
        json.dumps(
            {
                "run_id": str(run_id),
            }
        ),
    )


# ---------------------------------------
# Consumer
# ---------------------------------------

async def process_evaluation_queue():
    """
    Continuously processes evaluation jobs from Redis.
    """

    print("Evaluation worker waiting for jobs...")

    while True:

        try:

            _, raw_job = await redis_client.brpop(
                "evaluation_jobs"
            )

            job = json.loads(raw_job)

            run_id = job["run_id"]

            print(f"\nReceived evaluation job: {run_id}")

            run = await pipeline_runs.get_run(run_id)

            if run is None:
                print("Run not found.")
                continue

            print("Running evaluation...")

            await judge.evaluate(
                run_id=run["id"],
                query=run["query"],
                answer=run["generation"],
                context=run["prompt"],
            )

            print("Evaluation completed.\n")

        except Exception as e:

            print(
                f"Evaluation Worker Error: {e}"
            )