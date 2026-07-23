import asyncio
import json
import math

import redis.asyncio as redis

from backend.config import settings
from backend.providers.client import NeuroFlowClient
from backend.providers.router import ModelRouter
from backend.providers.openai_provider import OpenAIProvider
from backend.evaluation.metrics.faithfulness import FaithfulnessEvaluator


def pearson(x: list[float], y: list[float]) -> float:
    n = len(x)

    if n == 0:
        return 0.0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    numerator = sum(
        (a - mean_x) * (b - mean_y)
        for a, b in zip(x, y)
    )

    denominator = math.sqrt(
        sum((a - mean_x) ** 2 for a in x)
        * sum((b - mean_y) ** 2 for b in y)
    )

    if denominator == 0:
        return 0.0

    return numerator / denominator


async def main():

    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
    )

    router = ModelRouter(redis_client)

    client = NeuroFlowClient(
        router=router,
        redis_client=redis_client,
    )

    client.register_provider(
        "openai",
        OpenAIProvider(
            api_key=settings.OPENROUTER_API_KEY,
            model="meta-llama/llama-3.1-8b-instruct",
        ),
    )

    evaluator = FaithfulnessEvaluator(client)

    with open(
        "backend/evaluation/calibration/annotated_set.json",
        "r",
    ) as f:
        dataset = json.load(f)

    human_scores = []
    auto_scores = []

    print(f"\nRunning calibration on {len(dataset)} examples...\n")

    for index, sample in enumerate(dataset, start=1):

        auto_score = await evaluator.evaluate(
            query=sample["query"],
            answer=sample["answer"],
            context=sample["context"],
        )

        human_score = sample["human_score"]

        human_scores.append(human_score)
        auto_scores.append(auto_score)

        print("=" * 80)
        print(f"Example {index}/{len(dataset)}")
        print(f"Query : {sample['query']}")
        print(f"Human : {human_score}")
        print(f"Auto  : {auto_score}")

        if abs(human_score - auto_score) > 0.25:
            print("\n❌ MISMATCH DETECTED")
            print("-" * 80)
            print("Context:")
            print(sample["context"])
            print()
            print("Answer:")
            print(sample["answer"])
            print("-" * 80)

        print("=" * 80)
        print()

    correlation = pearson(
        human_scores,
        auto_scores,
    )

    result = {
        "pearson_correlation": correlation
    }

    with open(
        "backend/evaluation/calibration/calibration_results.json",
        "w",
    ) as f:
        json.dump(
            result,
            f,
            indent=4,
        )

    print("\nCalibration Complete")
    print(json.dumps(result, indent=4))

    await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())