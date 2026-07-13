import pytest

from backend.generation.generator import Generator


@pytest.mark.asyncio
async def test_generator():

    generator = Generator()

    answer = await generator.generate(
        question="What is NeuroFlow?",
        context="NeuroFlow is an enterprise Retrieval-Augmented Generation (RAG) platform.",
    )

    assert isinstance(answer, str)
    assert len(answer) > 10