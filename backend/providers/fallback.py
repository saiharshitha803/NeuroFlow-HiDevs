from .base import (
    BaseLLMProvider,
    ChatMessage,
    GenerationResult,
)


class FallbackChain:

    def __init__(
        self,
        providers: list[BaseLLMProvider],
    ):
        self.providers = providers


    async def complete(
        self,
        messages: list[ChatMessage],
        **kwargs,
    ) -> GenerationResult:

        last_error = None

        for provider in self.providers:

            try:

                return await provider.complete(
                    messages,
                    **kwargs
                )

            except Exception as error:

                last_error = error


        raise Exception(
            f"All providers failed: {last_error}"
        )


    async def stream(
        self,
        messages: list[ChatMessage],
        **kwargs,
    ):

        for provider in self.providers:

            try:

                async for token in provider.stream(
                    messages,
                    **kwargs
                ):
                    yield token

                return


            except Exception:

                continue


        raise Exception(
            "All providers failed during streaming"
        )


    async def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        last_error = None

        for provider in self.providers:

            try:

                return await provider.embed(
                    texts
                )


            except Exception as error:

                last_error = error


        raise Exception(
            f"Embedding failed: {last_error}"
        )