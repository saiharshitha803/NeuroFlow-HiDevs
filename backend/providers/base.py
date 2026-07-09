from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator


@dataclass
class ChatMessage:
    """
    Represents a single chat message exchanged with an LLM.
    """

    role: str
    content: str | list


@dataclass
class GenerationResult:
    """
    Standardized response returned by all LLM providers.
    """

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float
    finish_reason: str


class BaseLLMProvider(ABC):
    """
    Abstract base class that every LLM provider must implement.
    """

    @abstractmethod
    async def complete(
        self,
        messages: list[ChatMessage],
        **kwargs
    ) -> GenerationResult:
        """
        Generate a complete response.
        """
        pass

    @abstractmethod
    async def stream(
        self,
        messages: list[ChatMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream the response token by token.
        """
        pass

    @abstractmethod
    async def embed(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        """
        Generate embeddings for a list of texts.
        """
        pass

    @property
    @abstractmethod
    def cost_per_input_token(self) -> float:
        """
        Cost of one input token in USD.
        """
        pass

    @property
    @abstractmethod
    def cost_per_output_token(self) -> float:
        """
        Cost of one output token in USD.
        """
        pass

    @property
    @abstractmethod
    def context_window(self) -> int:
        """
        Maximum context window supported by the model.
        """
        pass