import pytest

from backend.pipeline.rag_pipeline import RAGPipeline


class MockChunk:
    def __init__(self, text):
        self.text = text


class MockRetriever:

    async def retrieve(self, question):
        return [
            MockChunk("NeuroFlow is an AI document processing system."),
            MockChunk("It uses Retrieval Augmented Generation.")
        ]


class MockGenerator:

    async def generate(self, question, context):
        return f"Answer based on: {context}"


@pytest.mark.asyncio
async def test_rag_pipeline_returns_answer():

    pipeline = RAGPipeline(
        retriever=MockRetriever(),
        generator=MockGenerator()
    )

    result = await pipeline.run(
        "What is NeuroFlow?"
    )

    assert "answer" in result
    assert "sources" in result
    assert "NeuroFlow" in result["answer"]


@pytest.mark.asyncio
async def test_rag_pipeline_retrieves_context():

    pipeline = RAGPipeline(
        retriever=MockRetriever(),
        generator=MockGenerator()
    )

    result = await pipeline.run(
        "Explain RAG"
    )

    assert len(result["sources"]) == 2