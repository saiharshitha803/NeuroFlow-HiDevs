from backend.providers.base import ChatMessage


class PromptBuilder:
    """
    Builds grounded prompts for RAG generation.

    Responsibilities:
    - Inject retrieved context
    - Apply query-type instructions
    - Enforce citation format
    - Add hidden reasoning instructions
    """

    BASE_SYSTEM_PROMPT = """
You are a precise research assistant.

Your task is to answer the user's question using ONLY the provided context.

Rules:

1. Do not use outside knowledge.
2. If the context is insufficient, explicitly say:
   "The provided context does not contain enough information."
3. Every factual statement must include citations.
4. Citations MUST follow this exact format:

[Source N]

where N refers to the numbered sources provided in the context.

5. Never create fake citations.
6. Never reference sources that are not present.

"""



    QUERY_TYPE_PROMPTS = {

        "factual": """
Provide a direct and concise answer.

If multiple sources contain the same information,
cite all relevant sources.
""",


        "analytical": """
Analyze and synthesize information across sources.

Identify:
- agreements
- differences
- contradictions

Before answering, reason internally step-by-step.
Do not expose your reasoning.
""",


        "comparative": """
Create a structured comparison.

Use tables when appropriate.

Compare only information available in the context.

Before answering, reason internally step-by-step.
Do not expose your reasoning.
""",


        "procedural": """
Provide numbered steps.

Every step must contain citations.
"""
    }



    def build_messages(
        self,
        query: str,
        context: str,
        query_type: str = "factual",
    ) -> list[ChatMessage]:

        instruction = self.QUERY_TYPE_PROMPTS.get(
            query_type,
            self.QUERY_TYPE_PROMPTS["factual"],
        )


        system_prompt = f"""
{self.BASE_SYSTEM_PROMPT}


Query type instructions:

{instruction}
"""


        user_prompt = f"""
<context>

{context}

</context>


User Question:

{query}
"""


        return [

            ChatMessage(
                role="system",
                content=system_prompt.strip(),
            ),


            ChatMessage(
                role="user",
                content=user_prompt.strip(),
            )

        ]