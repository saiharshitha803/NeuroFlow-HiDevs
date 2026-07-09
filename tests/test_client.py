import pytest

from backend.providers.client import NeuroFlowClient
from backend.providers.base import (
    ChatMessage,
    GenerationResult,
)
from backend.providers.router import RoutingCriteria


class FakeRedis:

    def __init__(self):
        self.data = {}


    async def incr(self, key):

        self.data[key] = (
            self.data.get(key, 0) + 1
        )


    async def incrbyfloat(
        self,
        key,
        value
    ):

        self.data[key] = (
            self.data.get(key, 0)
            + value
        )



class FakeRouter:

    async def route(
        self,
        criteria
    ):

        return {
            "model": "gpt-4o-mini",
            "provider": "openai"
        }



class FakeProvider:

    async def complete(
        self,
        messages,
        **kwargs
    ):

        return GenerationResult(

            content="Hello NeuroFlow",

            model="gpt-4o-mini",

            input_tokens=10,

            output_tokens=5,

            latency_ms=20,

            cost_usd=0.001,

            finish_reason="stop"
        )



@pytest.mark.asyncio
async def test_client_metrics():


    fake_redis = FakeRedis()


    client = NeuroFlowClient(

        router=FakeRouter(),

        redis_client=fake_redis
    )


    client.register_provider(
        "openai",
        FakeProvider()
    )



    messages = [

        ChatMessage(

            role="user",

            content="Hello"

        )

    ]



    result = await client.chat(

        messages,

        RoutingCriteria(
            task_type="rag_generation"
        )

    )



    assert result.content == "Hello NeuroFlow"



    assert (
        fake_redis.data[
            "metrics:model:gpt-4o-mini:calls"
        ]
        == 1
    )


    assert (
        fake_redis.data[
            "metrics:model:gpt-4o-mini:cost_usd"
        ]
        == 0.001
    )