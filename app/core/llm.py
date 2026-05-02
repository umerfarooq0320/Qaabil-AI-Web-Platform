"""
LLM client wrapper — abstracts OpenRouter/OpenAI API calls.
All agents use this module to talk to LLMs.
"""

import json
import logging
from openai import AsyncOpenAI
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Async OpenAI client pointed at OpenRouter
_llm_client: AsyncOpenAI | None = None


def get_llm_client() -> AsyncOpenAI:
    """Singleton async LLM client."""
    global _llm_client
    if _llm_client is None:
        _llm_client = AsyncOpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
        )
    return _llm_client


async def llm_query(
    prompt: str,
    model: str | None = None,
    system_prompt: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> str:
    """
    Send a prompt to the LLM and return the text response.

    Args:
        prompt: User message content
        model: Override default model
        system_prompt: Optional system message
        temperature: Creativity (0.0 = deterministic, 1.0 = creative)
        max_tokens: Max response length

    Returns:
        Raw text response from the LLM
    """
    client = get_llm_client()
    model = model or settings.DEFAULT_MODEL

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM query failed: {e}")
        raise


async def llm_json_query(
    prompt: str,
    model: str | None = None,
    system_prompt: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> dict | None:
    """
    Send a prompt and parse the response as JSON.
    Returns None if parsing fails.

    Uses lower temperature by default for structured output.
    """
    raw = await llm_query(
        prompt=prompt,
        model=model,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    if not raw:
        logger.warning("LLM returned empty response for JSON query.")
        return None

    # Try to extract JSON from the response
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Sometimes LLMs wrap JSON in markdown code blocks
        if "```json" in raw:
            json_str = raw.split("```json")[1].split("```")[0].strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        elif "```" in raw:
            json_str = raw.split("```")[1].split("```")[0].strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        logger.warning(f"Failed to parse LLM JSON response: {raw[:200]}")
        return None
