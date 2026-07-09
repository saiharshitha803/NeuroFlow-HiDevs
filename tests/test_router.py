import json
import pytest

from backend.providers.router import (
    ModelRouter,
    RoutingCriteria,
)


class FakeRedis:

    async def get(self, key):

        models = [
            {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "vision": True,
                "context": 128000,
                "fine_tuned": False,
                "judge": False,
                "estimated_cost": 0.0004,
            },
            {
                "provider": "anthropic",
                "model": "claude-haiku",
                "vision": False,
                "context": 200000,
                "fine_tuned": False,
                "judge": True,
                "estimated_cost": 0.001,
            }
        ]

        return json.dumps(models)



@pytest.mark.asyncio
async def test_vision_routing():

    router = ModelRouter(
        FakeRedis()
    )

    result = await router.route(
        RoutingCriteria(
            task_type="rag_generation",
            require_vision=True
        )
    )

    assert result["model"] == "gpt-4o-mini"