class Generator:
    """
    Mock Generator.
    """

    async def generate(
        self,
        question: str,
        context: str,
    ) -> str:

        return context