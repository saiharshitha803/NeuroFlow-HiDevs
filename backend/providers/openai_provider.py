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

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
    ):
        self.client = AsyncOpenAI(
            api_key=api_key
        )

        self.model = model


    @property
    def cost_per_input_token(self) -> float:

        return PRICE_TABLE[self.model]["input"]


    @property
    def cost_per_output_token(self) -> float:

        return PRICE_TABLE[self.model]["output"]


    @property
    def context_window(self) -> int:

        windows = {
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
        }

        return windows[self.model]


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
                    **kwargs,
                )


                latency = (
                    time.perf_counter() - start
                ) * 1000


                input_tokens = (
                    response
                    .usage
                    .prompt_tokens
                )

                output_tokens = (
                    response
                    .usage
                    .completion_tokens
                )


                cost = (
                    input_tokens *
                    self.cost_per_input_token
                    +
                    output_tokens *
                    self.cost_per_output_token
                )


                return GenerationResult(

                    content=response
                    .choices[0]
                    .message
                    .content,

                    model=self.model,

                    input_tokens=input_tokens,

                    output_tokens=output_tokens,

                    latency_ms=latency,

                    cost_usd=cost,

                    finish_reason=response
                    .choices[0]
                    .finish_reason,
                )


            except RateLimitError as e:


                wait = getattr(
                    e,
                    "retry_after",
                    2 ** attempt
                )

                await asyncio.sleep(wait)


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

            **kwargs,
        )


        async for chunk in response:


            if not chunk.choices:
                continue


            token = (
                chunk
                .choices[0]
                .delta
                .content
            )


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
            batch_size
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