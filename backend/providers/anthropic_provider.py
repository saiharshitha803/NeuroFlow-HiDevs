import asyncio
import time
from typing import AsyncGenerator

from anthropic import AsyncAnthropic, RateLimitError

from .base import (
    BaseLLMProvider,
    ChatMessage,
    GenerationResult,
)
from .pricing import PRICE_TABLE


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude provider implementation.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-haiku",
    ):
        self.client = AsyncAnthropic(api_key=api_key)
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
            "claude-3-haiku": 200000,
            "claude-3-sonnet": 200000,
        }
        return windows[self.model]

    async def complete(
        self,
        messages: list[ChatMessage],
        **kwargs,
    ) -> GenerationResult:

        system_prompt = ""
        anthropic_messages = []

        for message in messages:

            if message.role == "system":
                if isinstance(message.content, str):
                    system_prompt += message.content
                else:
                    system_prompt += str(message.content)

            else:
                anthropic_messages.append(
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                )

        last_error = None

        for attempt in range(3):

            try:

                start = time.perf_counter()

                response = await self.client.messages.create(
                    model=self.model,
                    system=system_prompt,
                    messages=anthropic_messages,
                    max_tokens=kwargs.pop("max_tokens", 1024),
                    **kwargs,
                )

                latency = (time.perf_counter() - start) * 1000

                content = ""

                for block in response.content:
                    if getattr(block, "type", "") == "text":
                        content += block.text

                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens

                cost = (
                    input_tokens * self.cost_per_input_token
                    + output_tokens * self.cost_per_output_token
                )

                return GenerationResult(
                    content=content,
                    model=self.model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    latency_ms=latency,
                    cost_usd=cost,
                    finish_reason=response.stop_reason or "stop",
                )

            except RateLimitError as e:

                last_error = e

                wait = getattr(
                    e,
                    "retry_after",
                    2 ** attempt,
                )

                await asyncio.sleep(wait)

        raise last_error

    async def stream(
        self,
        messages: list[ChatMessage],
        **kwargs,
    ) -> AsyncGenerator[str, None]:

        system_prompt = ""
        anthropic_messages = []

        for message in messages:

            if message.role == "system":
                if isinstance(message.content, str):
                    system_prompt += message.content
                else:
                    system_prompt += str(message.content)

            else:
                anthropic_messages.append(
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                )

        stream = await self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=anthropic_messages,
            max_tokens=kwargs.pop("max_tokens", 1024),
            stream=True,
            **kwargs,
        )

        async for event in stream:

            if (
                event.type == "content_block_delta"
                and event.delta.type == "text_delta"
            ):
                yield event.delta.text

    async def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Anthropic currently does not expose
        a public embeddings endpoint.
        """
        raise NotImplementedError(
            "Anthropic provider does not support embeddings."
        )