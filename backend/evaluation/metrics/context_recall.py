import asyncio

from backend.providers.client import NeuroFlowClient
from backend.providers.base import ChatMessage
from backend.providers.router import RoutingCriteria


class ContextRecallEvaluator:

    def __init__(
        self,
        client: NeuroFlowClient,
    ):
        self.client = client

    async def _judge_sentence(
        self,
        sentence: str,
        context: str,
    ) -> float:

        prompt = f"""
Context:

{context}

Sentence:

{sentence}

Can this sentence be attributed to the context?

Answer ONLY:

yes

or

no
"""

        result = await self.client.chat(
            messages=[
                ChatMessage(
                    role="user",
                    content=prompt,
                )
            ],
            routing_criteria=RoutingCriteria(
                task_type="evaluation",
            ),
        )

        verdict = result.content.lower().strip()

        if "yes" in verdict:
            return 1.0

        return 0.0

    async def evaluate(
        self,
        query: str,
        chunks: list[str],
        answer: str,
    ) -> float:

        if not answer.strip():
            return 0.0

        context = "\n\n".join(chunks)

        sentences = [
            sentence.strip()
            for sentence in answer.split(".")
            if sentence.strip()
        ]

        if not sentences:
            return 0.0

        results = await asyncio.gather(
            *[
                self._judge_sentence(
                    sentence,
                    context,
                )
                for sentence in sentences
            ]
        )

        return sum(results) / len(results)