import json
import math

from backend.providers.client import NeuroFlowClient
from backend.providers.base import ChatMessage
from backend.providers.router import RoutingCriteria


class AnswerRelevanceEvaluator:

    def __init__(
        self,
        client: NeuroFlowClient,
    ):
        self.client = client

    async def _generate_questions(
        self,
        answer: str,
    ) -> list[str]:

        prompt = f"""
Generate 3 questions that this answer could answer.

Return ONLY a JSON array.

Answer:

{answer}
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

        try:
            return json.loads(result.content)
        except Exception:
            return []

    def _cosine_similarity(
        self,
        a: list[float],
        b: list[float],
    ) -> float:

        dot = sum(x * y for x, y in zip(a, b))

        norm_a = math.sqrt(
            sum(x * x for x in a)
        )

        norm_b = math.sqrt(
            sum(y * y for y in b)
        )

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    async def evaluate(
        self,
        query: str,
        answer: str,
    ) -> float:

        questions = await self._generate_questions(
            answer
        )

        if not questions:
            return 0.0

        embeddings = await self.client.embed(
            [query] + questions
        )

        query_embedding = embeddings[0]

        similarities = []

        for embedding in embeddings[1:]:

            similarities.append(
                self._cosine_similarity(
                    query_embedding,
                    embedding,
                )
            )

        return sum(similarities) / len(similarities)