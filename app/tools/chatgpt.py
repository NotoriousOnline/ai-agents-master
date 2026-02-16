"""ChatGPT (OpenAI API) tool for agents. Uses OPENAI_API_KEY from settings."""

from app.config import get_settings


async def chatgpt_complete(
    prompt: str,
    *,
    model: str = "gpt-4o-mini",
    max_tokens: int = 1024,
) -> str:
    """
    Send a prompt to ChatGPT and return the assistant reply.
    Requires OPENAI_API_KEY in .env.
    """
    settings = get_settings()
    if not settings.openai_api_key:
        return "[ChatGPT not configured: set OPENAI_API_KEY in .env]"

    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    if response.choices and response.choices[0].message.content is not None:
        return response.choices[0].message.content
    return ""
