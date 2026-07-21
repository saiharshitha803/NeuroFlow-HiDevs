import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables from .env
load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "NeuroFlow",
    },
)


async def main():
    response = await client.chat.completions.create(
        model="meta-llama/llama-3.1-8b-instruct",
        messages=[
            {
                "role": "user",
                "content": "Say hello in one sentence.",
            }
        ],
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    asyncio.run(main())