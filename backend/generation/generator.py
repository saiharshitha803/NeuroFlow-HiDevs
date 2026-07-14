from typing import Optional

from backend.providers.base import (
    ChatMessage,
)

from backend.providers.client import NeuroFlowClient


class Generator:
    """
    RAG Answer Generator.

    Converts retrieved context into
    final user-facing answers.

    Supports:
    - LLM providers
    - fallback mode
    """


    def __init__(
        self,
        llm_client: Optional[NeuroFlowClient] = None,
    ):

        self.llm_client = llm_client



    async def generate(
        self,
        question: str,
        context: str,
        **kwargs,
    ) -> str:
        """
        Generate answer using retrieved context.
        """


        prompt = f"""
You are NeuroFlow AI assistant.

Answer the user question using ONLY
the provided context.

If the answer is not present,
say:
"I don't have enough information."

Context:
----------------
{context}
----------------


Question:
{question}


Answer:
"""


        # If LLM client exists
        if self.llm_client:


            messages = [

                ChatMessage(
                    role="system",
                    content=(
                        "You are a helpful "
                        "retrieval augmented assistant."
                    ),
                ),


                ChatMessage(
                    role="user",
                    content=prompt,
                ),
            ]


            result = await self.llm_client.chat(
                messages,
                **kwargs,
            )


            return result.content



        # Local fallback
        return self._fallback_answer(
            question,
            context,
        )



    def _fallback_answer(
        self,
        question: str,
        context: str,
    ) -> str:
        """
        Simple fallback generator.

        Used when no external LLM
        is configured.
        """


        if not context:

            return (
                "I don't have enough information "
                "to answer this question."
            )


        return (
            "Based on the retrieved information:\n\n"
            + context
        )