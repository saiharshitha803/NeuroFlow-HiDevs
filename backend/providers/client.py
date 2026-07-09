import time
from typing import Dict

import redis.asyncio as redis

from opentelemetry import trace

from .base import (
    ChatMessage,
    GenerationResult,
    BaseLLMProvider,
)

from .router import (
    ModelRouter,
    RoutingCriteria,
)


class NeuroFlowClient:

    _instance = None


    def __new__(
        cls,
        *args,
        **kwargs
    ):

        if cls._instance is None:

            cls._instance = super().__new__(
                cls
            )

        return cls._instance



    def __init__(
        self,
        router: ModelRouter,
        redis_client: redis.Redis,
    ):

        self.router = router

        self.redis = redis_client

        self.providers: Dict[
            str,
            BaseLLMProvider
        ] = {}

        self.tracer = trace.get_tracer(
            "neuroflow"
        )



    def register_provider(
        self,
        name: str,
        provider: BaseLLMProvider,
    ):

        self.providers[name] = provider



    async def chat(
        self,
        messages: list[ChatMessage],
        routing_criteria: RoutingCriteria,
        **kwargs,
    ) -> GenerationResult:


        # 1. Select model using router

        selected_model = await self.router.route(
            routing_criteria
        )


        model_name = selected_model["model"]

        provider_name = selected_model["provider"]



        # 2. Find provider

        provider = self.providers.get(
            provider_name
        )


        if provider is None:

            raise ValueError(
                f"Provider {provider_name} not registered"
            )



        # 3. OpenTelemetry span

        with self.tracer.start_as_current_span(
            "llm.chat"
        ) as span:


            start = time.perf_counter()



            # 4. Execute LLM call

            result = await provider.complete(
                messages,
                **kwargs,
            )



            latency = (
                time.perf_counter()
                -
                start
            ) * 1000



            # 5. Add tracing attributes


            span.set_attribute(
                "model",
                model_name
            )


            span.set_attribute(
                "input_tokens",
                result.input_tokens
            )


            span.set_attribute(
                "output_tokens",
                result.output_tokens
            )


            span.set_attribute(
                "cost_usd",
                result.cost_usd
            )


            span.set_attribute(
                "latency_ms",
                latency
            )



        # 6. Redis metrics


        await self.redis.incr(
            f"metrics:model:{model_name}:calls"
        )


        await self.redis.incrbyfloat(
            f"metrics:model:{model_name}:cost_usd",
            result.cost_usd
        )



        return result




    async def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:



        provider = None



        # Find embedding provider

        for registered_provider in self.providers.values():


            if hasattr(
                registered_provider,
                "embed"
            ):

                provider = registered_provider

                break




        if provider is None:

            raise ValueError(
                "No embedding provider registered"
            )



        with self.tracer.start_as_current_span(
            "llm.embed"
        ) as span:



            start = time.perf_counter()



            embeddings = await provider.embed(
                texts
            )



            latency = (
                time.perf_counter()
                -
                start
            ) * 1000




            span.set_attribute(
                "operation",
                "embedding"
            )


            span.set_attribute(
                "input_text_count",
                len(texts)
            )


            span.set_attribute(
                "latency_ms",
                latency
            )



        return embeddings