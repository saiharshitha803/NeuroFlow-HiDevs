import pytest

from backend.embeddings.provider import EmbeddingProvider


@pytest.mark.asyncio
async def test_embedding_provider():

    provider = EmbeddingProvider()

    embedding = await provider.embed(
        "Hello NeuroFlow"
    )

    assert isinstance(embedding, list)

    assert len(embedding) > 100

    assert isinstance(embedding[0], float)