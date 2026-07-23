import json
import math
import re
from typing import Any


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """
    Compute cosine similarity between two vectors.

    Returns a value in [0, 1].
    """

    if len(vector_a) != len(vector_b):
        raise ValueError("Embedding dimensions do not match.")

    dot = sum(a * b for a, b in zip(vector_a, vector_b))

    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    similarity = dot / (norm_a * norm_b)

    return max(0.0, min(1.0, similarity))


def extract_json(
    text: str,
) -> Any:
    """
    Extract JSON from an LLM response.

    Handles:
    - plain JSON
    - ```json ... ```
    - ``` ... ```
    """

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    return json.loads(text)


def split_sentences(
    text: str,
) -> list[str]:
    """
    Split text into sentences.
    """

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip(),
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


async def call_llm(
    *args,
    **kwargs,
):
    """
    Placeholder.

    Implemented during Phase 3 when
    EvaluationJudge is built.
    """

    raise NotImplementedError


async def embed_text(
    *args,
    **kwargs,
):
    """
    Placeholder.

    Implemented during Phase 3.
    """

    raise NotImplementedError