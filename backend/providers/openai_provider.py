import asyncio
import time
from typing import AsyncGenerator

from openai import AsyncOpenAI, RateLimitError

from .base import (
    BaseLLMProvider,
    ChatMessage,
    GenerationResult,
)

from .pricing import PRICE_TABLE


class OpenAIProvider(BaseLLMProvider):
    """
    OpenRouter implementation using the OpenAI SDK.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "meta-llama/llama-3.1-8b-instruct:free",
    ):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

        self.model = model

    @property
    def cost_per_input_token(self) -> float:
        return PRICE_TABLE.get(
            self.model,
            {
                "input": 0.0,
                "output": 0.0,
            },
        )["input"]

    @property
    def cost_per_output_token(self) -> float:
        return PRICE_TABLE.get(
            self.model,
            {
                "input": 0.0,
                "output": 0.0,
            },
        )["output"]

    @property
    def context_window(self) -> int:
        return 128000

    async def complete(
        self,
        messages: list[ChatMessage],
        **kwargs,
    ) -> GenerationResult:

        payload = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

        for attempt in range(3):

            try:

                start = time.perf_counter()

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=payload,
                    extra_headers={
                        "HTTP-Referer": "https://github.com/saiharshitha803/NeuroFlow-HiDevs",
                        "X-Title": "NeuroFlow",
                    },
                    **kwargs,
                )

                latency = (
                    time.perf_counter() - start
                ) * 1000

                usage = response.usage

                input_tokens = (
                    usage.prompt_tokens
                    if usage
                    else 0
                )

                output_tokens = (
                    usage.completion_tokens
                    if usage
                    else 0
                )

                cost = (
                    input_tokens
                    * self.cost_per_input_token
                    +
                    output_tokens
                    * self.cost_per_output_token
                )

                return GenerationResult(
                    content=response.choices[0].message.content,
                    model=self.model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    latency_ms=latency,
                    cost_usd=cost,
                    finish_reason=response.choices[0].finish_reason,
                )

            except RateLimitError as e:

                print("\n========================")
                print("RATE LIMIT")
                print("========================")
                print(e)

                wait = getattr(
                    e,
                    "retry_after",
                    2 ** attempt,
                )

                await asyncio.sleep(wait)

            except Exception as e:

                print("\n========================")
                print("OPENROUTER ERROR")
                print("========================")
                print(type(e).__name__)
                print(e)
                print("========================")

                raise

        raise Exception(
            "Maximum retry attempts exceeded."
        )

    async def stream(
        self,
        messages: list[ChatMessage],
        **kwargs,
    ) -> AsyncGenerator[str, None]:

        payload = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=payload,
            stream=True,
            extra_headers={
                "HTTP-Referer": "https://github.com/saiharshitha803/NeuroFlow-HiDevs",
                "X-Title": "NeuroFlow",
            },
            **kwargs,
        )

        async for chunk in response:

            if not chunk.choices:
                continue

            token = chunk.choices[0].delta.content

            if token:
                yield token

    async def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        embeddings = []

        batch_size = 100

        for i in range(
            0,
            len(texts),
            batch_size,
        ):

            batch = texts[
                i:i + batch_size
            ]

            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=batch,
            )

            embeddings.extend(
                item.embedding
                for item in response.data
            )

        return embeddings