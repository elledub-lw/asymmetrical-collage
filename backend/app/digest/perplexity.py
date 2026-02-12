"""
Perplexity API client for news gathering.
Implements retry logic and batched queries.
"""

import asyncio
import httpx
from typing import Optional


PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = "sonar"

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAYS = [2, 4, 8]  # Exponential backoff in seconds

# Batching configuration
BATCH_SIZE = 3
BATCH_PAUSE_SECONDS = 2


async def search_with_perplexity(
    query: str,
    system_prompt: str,
    api_key: str,
) -> Optional[str]:
    """
    Execute a single search query against Perplexity API.

    Args:
        query: The search query
        system_prompt: System prompt with time constraints
        api_key: Perplexity API key

    Returns:
        Response text or None if failed
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        "search_recency_filter": "day",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.post(
                    PERPLEXITY_API_URL,
                    headers=headers,
                    json=payload,
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    return content if content else None

                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(RETRY_DELAYS[attempt])
                        continue
                    else:
                        print(f"Perplexity rate limit exceeded after {MAX_RETRIES} attempts")
                        return None

                else:
                    print(f"Perplexity API error: {response.status_code} - {response.text}")
                    return None

            except httpx.TimeoutException:
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAYS[attempt])
                    continue
                print(f"Perplexity request timed out after {MAX_RETRIES} attempts")
                return None

            except Exception as e:
                print(f"Perplexity request error: {e}")
                return None

    return None


async def gather_news(
    queries: list[tuple[str, str]],
    system_prompt: str,
    api_key: str,
) -> tuple[str, list[dict]]:
    """
    Execute all queries in batches and combine results.

    Args:
        queries: List of (query, category) tuples
        system_prompt: System prompt with time constraints
        api_key: Perplexity API key

    Returns:
        Tuple of (combined_news_text, sources_list)
    """
    all_results: list[str] = []
    sources: list[dict] = []

    # Process in batches
    for i in range(0, len(queries), BATCH_SIZE):
        batch = queries[i:i + BATCH_SIZE]

        # Run batch in parallel
        tasks = [
            search_with_perplexity(query, system_prompt, api_key)
            for query, _ in batch
        ]
        results = await asyncio.gather(*tasks)

        # Collect non-empty results
        for (query, category), result in zip(batch, results):
            if result and result.strip() and "No news found" not in result:
                all_results.append(f"[Category: {category}]\n{result}")

                # Extract any URLs mentioned (basic extraction)
                # More sophisticated extraction could be added
                sources.append({
                    "query": query,
                    "category": category,
                    "has_results": True,
                })

        # Pause between batches to respect rate limits
        if i + BATCH_SIZE < len(queries):
            await asyncio.sleep(BATCH_PAUSE_SECONDS)

    # Combine all results
    combined = "\n\n---\n\n".join(all_results) if all_results else "No news found in the last 24 hours across all categories."

    return combined, sources
