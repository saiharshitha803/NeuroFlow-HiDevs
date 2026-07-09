"""
Pricing information for supported LLM models.

Prices are in USD per TOKEN (converted from USD per 1M tokens).
"""

PRICE_TABLE = {

    # ---------------------------
    # OpenAI Models
    # ---------------------------

    "gpt-4o": {
        "input": 2.50 / 1_000_000,
        "output": 10.00 / 1_000_000,
    },

    "gpt-4o-mini": {
        "input": 0.15 / 1_000_000,
        "output": 0.60 / 1_000_000,
    },

    # ---------------------------
    # Anthropic Models
    # ---------------------------

    "claude-3-haiku": {
        "input": 0.25 / 1_000_000,
        "output": 1.25 / 1_000_000,
    },

    "claude-3-sonnet": {
        "input": 3.00 / 1_000_000,
        "output": 15.00 / 1_000_000,
    },

}