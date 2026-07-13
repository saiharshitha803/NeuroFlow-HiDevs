import hashlib
import random


class EmbeddingProvider:
    """
    Deterministic embedding provider for testing.

    Generates the same embedding for the same text
    without requiring an external API.
    """

    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    async def embed(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate a deterministic embedding.
        """

        seed = int(
            hashlib.sha256(text.encode()).hexdigest(),
            16,
        )

        rng = random.Random(seed)

        return [
            rng.uniform(-1.0, 1.0)
            for _ in range(self.dimension)
        ]