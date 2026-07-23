import asyncio
import json
import re

from backend.providers.base import ChatMessage
from backend.providers.client import NeuroFlowClient
from backend.providers.router import RoutingCriteria


class FaithfulnessEvaluator:

    def __init__(
        self,
        client: NeuroFlowClient,
    ):
        self.client = client

    async def _extract_claims(
        self,
        answer: str,
    ) -> list[str]:

        answer = answer.strip()

        # -------------------------------------------------------
        # Single sentence?
        # Just use it directly.
        # -------------------------------------------------------

        sentences = [
            s.strip()
            for s in re.split(
                r"[.!?]+",
                answer,
            )
            if s.strip()
        ]

        if len(sentences) == 1:
            return [answer]

        prompt = f"""
You are an information extraction system.

Extract every factual claim from the ANSWER.

Rules:

- Return ONLY a JSON array.
- Every element must be a string.
- Do not explain.
- Do not answer the question.
- Do not ask for more input.
- Do not use markdown.
- Never return anything except JSON.

ANSWER:

{answer}

JSON:
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

        raw = result.content.strip()

        print("\n====================")
        print("CLAIM EXTRACTION RAW OUTPUT")
        print(raw)
        print("====================")

        # -------------------------------------------------------
        # Find JSON array
        # -------------------------------------------------------

        match = re.search(
            r"\[[\s\S]*\]",
            raw,
        )

        if match:
            raw = match.group(0)

        try:

            claims = json.loads(raw)

            claims = [
                c.strip()
                for c in claims
                if isinstance(c, str)
            ]

        except Exception:

            print("JSON parsing failed. Using answer as fallback.")

            claims = [answer]

        # -------------------------------------------------------
        # Clean garbage
        # -------------------------------------------------------

        cleaned = []

        for claim in claims:

            claim = claim.strip()

            if claim in {
                "{",
                "}",
                "[",
                "]",
            }:
                continue

            if len(claim) < 3:
                continue

            cleaned.append(claim)

        if not cleaned:
            cleaned = [answer]

        print("\nRecovered Claims")
        print(cleaned)

        return cleaned

    async def _judge_claim(
        self,
        claim: str,
        context: str,
    ) -> float:

        prompt = f"""
You are evaluating factual consistency.

Context:

{context}

Claim:

{claim}

Return ONLY one word.

supported

or

partial

or

contradicted
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

        print("\nLLM Verdict")
        print(verdict)

        if "contrad" in verdict:
            return 0.0

        if "partial" in verdict:
            return 0.5

        if "support" in verdict:
            return 1.0

        return 0.0

    async def evaluate(
        self,
        query: str,
        answer: str,
        context: str,
    ) -> float:

        if not context.strip():

            if answer.strip():
                return 0.0

            return 1.0

        claims = await self._extract_claims(
            answer
        )

        print("\n====================")
        print("ANSWER")
        print(answer)
        print("--------------------")
        print("CLAIMS")
        print(claims)
        print("====================")

        scores = []

        for claim in claims:

            score = await self._judge_claim(
                claim,
                context,
            )

            print(f"\nClaim : {claim}")
            print(f"Score : {score}")

            scores.append(score)

        if not scores:
            return 0.0

        final = sum(scores) / len(scores)

        print(f"\nFINAL FAITHFULNESS = {final}\n")

        return final