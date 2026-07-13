from backend.retrieval.retriever import Retriever
from backend.generation.generator import Generator


class RAGPipeline:
    """
    End-to-end Retrieval Augmented Generation pipeline.
    """

    def __init__(self, retriever=None, generator=None):
        self.retriever = retriever or Retriever()
        self.generator = generator or Generator()

    async def run(self, query: str):
        # Retrieve relevant chunks
        chunks = await self.retriever.retrieve(query)

        # Build context
        context_parts = []

        for chunk in chunks:

            # Dictionary returned from database
            if isinstance(chunk, dict):
                context_parts.append(chunk.get("content", ""))

            # Object with .content
            elif hasattr(chunk, "content"):
                context_parts.append(chunk.content)

            # Object with .text
            elif hasattr(chunk, "text"):
                context_parts.append(chunk.text)

            else:
                context_parts.append(str(chunk))

        context = "\n\n".join(context_parts)

        # Generate answer
        answer = await self.generator.generate(
            question=query,
            context=context,
        )

        # Build sources
        sources = []

        for chunk in chunks:
            if isinstance(chunk, dict):
                sources.append(
                    chunk.get("source")
                    or chunk.get("metadata")
                    or chunk.get("content")
                    or chunk.get("text")
                )
            else:
                if hasattr(chunk, "source"):
                    sources.append(chunk.source)
                elif hasattr(chunk, "metadata"):
                    sources.append(chunk.metadata)
                elif hasattr(chunk, "content"):
                    sources.append(chunk.content)
                elif hasattr(chunk, "text"):
                    sources.append(chunk.text)
                else:
                    sources.append(str(chunk))

        return {
            "query": query,
            "answer": answer,
            "context": context,
            "sources": sources,
        }