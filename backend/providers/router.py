import json
from dataclasses import dataclass
from typing import Any

import redis.asyncio as redis


@dataclass
class RoutingCriteria:
    task_type: str
    max_cost_per_call: float | None = None
    require_vision: bool = False
    require_long_context: bool = False
    latency_budget_ms: int | None = None
    prefer_fine_tuned: bool = False


class ModelRouter:

    def __init__(
        self,
        redis_client: redis.Redis,
    ):
        self.redis = redis_client


    async def _load_models(
        self,
    ) -> list[dict[str, Any]]:

        data = await self.redis.get("router:models")

        if not data:
            return []

        return json.loads(data)


    async def route(
        self,
        criteria: RoutingCriteria,
    ) -> dict[str, Any]:

        models = await self._load_models()

        candidates = models.copy()


        # Rule 1: Vision requirement
        if criteria.require_vision:

            candidates = [
                model
                for model in candidates
                if model.get("vision", False)
            ]


        # Rule 2: Long context requirement
        if criteria.require_long_context:

            candidates = [
                model
                for model in candidates
                if model.get("context", 0) > 100000
            ]


        # Rule 3: Prefer fine-tuned model
        if criteria.prefer_fine_tuned:

            fine_tuned_models = [
                model
                for model in candidates
                if (
                    model.get("fine_tuned", False)
                    and model.get("task_type") == criteria.task_type
                )
            ]

            if fine_tuned_models:
                candidates = fine_tuned_models


        # Rule 4: Evaluation requires judge model
        if criteria.task_type == "evaluation":

            candidates = [
                model
                for model in candidates
                if (
                    model.get("judge", False)
                    and not model.get("fine_tuned", False)
                )
            ]


        # Rule 5: Cost constraint
        if criteria.max_cost_per_call is not None:

            candidates = [
                model
                for model in candidates
                if model.get(
                    "estimated_cost",
                    float("inf")
                )
                <= criteria.max_cost_per_call
            ]


        if not candidates:
            raise ValueError(
                "No model satisfies the routing requirements."
            )


        # Default: cheapest model
        candidates.sort(
            key=lambda model: model.get(
                "estimated_cost",
                float("inf")
            )
        )


        return candidates[0]