import pytest

from backend.providers.openai_provider import OpenAIProvider
from backend.providers.base import ChatMessage


class FakeStream:

    def __aiter__(self):
        return self


    async def __anext__(self):

        tokens = [
            "Hello",
            " ",
            "NeuroFlow"
        ]

        if hasattr(self, "index") is False:
            self.index = 0


        if self.index >= len(tokens):
            raise StopAsyncIteration


        token = tokens[self.index]

        self.index += 1


        class Delta:
            content = token


        class Choice:
            delta = Delta()


        class Chunk:
            choices = [Choice()]


        return Chunk()



@pytest.mark.asyncio
async def test_stream(monkeypatch):


    provider = OpenAIProvider(
        api_key="fake-key",
        model="gpt-4o-mini"
    )


    async def fake_create(*args, **kwargs):

        return FakeStream()



    monkeypatch.setattr(
        provider.client.chat.completions,
        "create",
        fake_create
    )


    messages = [
        ChatMessage(
            role="user",
            content="Say hello"
        )
    ]


    tokens = []


    async for token in provider.stream(messages):

        tokens.append(token)


    assert tokens == [
        "Hello",
        " ",
        "NeuroFlow"
    ]