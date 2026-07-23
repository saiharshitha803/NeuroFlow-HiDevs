import asyncio

from backend.providers.client import NeuroFlowClient
from backend.providers.base import ChatMessage
from backend.providers.router import RoutingCriteria


class ContextPrecisionEvaluator:

    def __init__(
        self,
        client: NeuroFlowClient,
    ):
        self.client = client

    async def _judge_chunk(
        self,
        query: str,
        chunk: str,
        answer: str,
    ) -> float:

        prompt = f"""
Query:

{query}

Retrieved Passage:

{chunk}

Generated Answer:

{answer}

Was this passage useful in generating the answer?

Answer ONLY one word:

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

        if not chunks:
            return 0.0

        useful = await asyncio.gather(
            *[
                self._judge_chunk(
                    query,
                    chunk,
                    answer,
                )
                for chunk in chunks
            ]
        )

        weighted_sum = 0.0
        total_weight = 0.0

        for rank, score in enumerate(
            useful,
            start=1,
        ):

            weight = 1 / rank

            weighted_sum += (
                score * weight
            )

            total_weight += weight
        if total_weight == 0:
         return 0.0
    
        return weighted_sum / total_weight