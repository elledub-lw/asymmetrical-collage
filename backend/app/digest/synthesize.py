"""
Claude API synthesis for Market Watch newsletter.
Generates digest from gathered news with model fallback.
"""

import json
import httpx
from typing import Optional

from .prompts import DIGEST_SYSTEM_PROMPT, get_digest_user_prompt, CATEGORIZATION_PROMPT
from .validate import validate_content, sanitize_content
from .sources import VALID_CATEGORIES


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
PRIMARY_MODEL = "claude-sonnet-4-20250514"
FALLBACK_MODEL = "claude-3-5-haiku-20241022"

# Token limits
MAX_TOKENS = 4096
TIMEOUT_SECONDS = 120


async def call_claude(
    system_prompt: str,
    user_prompt: str,
    api_key: str,
    model: str = PRIMARY_MODEL,
    max_tokens: int = MAX_TOKENS,
) -> Optional[str]:
    """
    Call Claude API with the given prompts.

    Args:
        system_prompt: System prompt for Claude
        user_prompt: User prompt with the actual request
        api_key: Anthropic API key
        model: Model to use
        max_tokens: Maximum tokens in response

    Returns:
        Response text or None if failed
    """
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_prompt}
        ],
    }

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        try:
            response = await client.post(
                ANTHROPIC_API_URL,
                headers=headers,
                json=payload,
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [])
                if content and len(content) > 0:
                    return content[0].get("text", "")
                return None
            else:
                print(f"Claude API error: {response.status_code} - {response.text}")
                return None

        except httpx.TimeoutException:
            print(f"Claude API timeout after {TIMEOUT_SECONDS}s")
            return None
        except Exception as e:
            print(f"Claude API error: {e}")
            return None


async def synthesize_digest(
    news_content: str,
    today_str: str,
    start_iso: str,
    end_iso: str,
    api_key: str,
) -> tuple[Optional[str], Optional[str]]:
    """
    Generate the digest using Claude API with model fallback.

    Args:
        news_content: Combined news from Perplexity
        today_str: Formatted date string (e.g., "February 12, 2026")
        start_iso: Start of time window
        end_iso: End of time window
        api_key: Anthropic API key

    Returns:
        Tuple of (digest_content, error_message)
    """
    user_prompt = get_digest_user_prompt(today_str, start_iso, end_iso, news_content)

    # Try primary model first
    result = await call_claude(
        DIGEST_SYSTEM_PROMPT,
        user_prompt,
        api_key,
        model=PRIMARY_MODEL,
    )

    # Fallback to secondary model if primary fails
    if not result:
        print(f"Primary model {PRIMARY_MODEL} failed, trying fallback {FALLBACK_MODEL}")
        result = await call_claude(
            DIGEST_SYSTEM_PROMPT,
            user_prompt,
            api_key,
            model=FALLBACK_MODEL,
        )

    if not result:
        return None, "Failed to generate digest with both primary and fallback models"

    # Validate the generated content
    is_valid, error = validate_content(result)
    if not is_valid:
        # Try to sanitize
        sanitized = sanitize_content(result)
        is_valid_sanitized, _ = validate_content(sanitized)
        if is_valid_sanitized:
            return sanitized, None
        return None, f"Content validation failed: {error}"

    return result, None


async def categorize_digest(
    content: str,
    api_key: str,
) -> list[str]:
    """
    Analyze digest and return list of categories with actual content.

    Args:
        content: The generated digest markdown
        api_key: Anthropic API key

    Returns:
        List of category slugs that have news items
    """
    prompt = CATEGORIZATION_PROMPT.format(content=content)

    result = await call_claude(
        "You are a helpful assistant that outputs only valid JSON.",
        prompt,
        api_key,
        model=FALLBACK_MODEL,  # Use cheaper model for categorization
        max_tokens=256,
    )

    if not result:
        # Default to empty list if categorization fails
        return []

    # Parse JSON response
    try:
        # Clean up response - sometimes models add markdown code blocks
        cleaned = result.strip()
        if cleaned.startswith("```"):
            # Remove code block markers
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        categories = json.loads(cleaned)

        # Validate categories
        if isinstance(categories, list):
            return [c for c in categories if c in VALID_CATEGORIES]
        return []

    except json.JSONDecodeError:
        print(f"Failed to parse categorization response: {result}")
        return []
