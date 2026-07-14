import asyncio
from typing import Any

from sentence_transformers import CrossEncoder



class CrossEncoderReranker:
    """
    Cross Encoder based reranking.

    Reranks RRF candidates by scoring:

        (query, chunk)

    pairs together.
    """



    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):

        self.model = CrossEncoder(
            model_name
        )



    async def rerank(
        self,
        query: str,
        candidates: list[Any],
        top_k: int = 10,
    ) -> list[Any]:
        """
        Rerank retrieved candidates.

        Input:
            RRF fused candidates

        Output:
            Top-k ranked chunks
        """


        if not candidates:

            return []



        pairs = [

            (
                query,
                chunk.content
            )

            for chunk in candidates

        ]



        # Run model outside async event loop
        scores = await asyncio.to_thread(
            self.model.predict,
            pairs
        )



        for chunk, score in zip(
            candidates,
            scores
        ):

            chunk.score = float(
                score
            )



        ranked = sorted(
            candidates,
            key=lambda x: x.score,
            reverse=True
        )


        return ranked[:top_k]



    async def score(
        self,
        query: str,
        passage: str,
    ) -> float:
        """
        Score one query-passage pair.
        """


        result = await asyncio.to_thread(
            self.model.predict,
            [
                (
                    query,
                    passage
                )
            ]
        )


        return float(
            result[0]
        )