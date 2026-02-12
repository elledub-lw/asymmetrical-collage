"""
Content safety validation for Market Watch newsletter.
Prevents injection of scripts, HTML, and other unsafe content.
"""

import re
from typing import Optional


# Security patterns to reject
DANGEROUS_PATTERNS = [
    r"<script[^>]*>",
    r"</script>",
    r"javascript:",
    r"on\w+\s*=",  # onclick=, onerror=, etc.
    r"<iframe",
    r"<object",
    r"<embed",
    r"<form",
    r"data:",  # data: URLs
    r"vbscript:",
    r"<meta",
    r"<link[^>]*>",
    r"<style[^>]*>",
]

# Compiled patterns for efficiency
COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in DANGEROUS_PATTERNS]

# Allowed markdown patterns
ALLOWED_MARKDOWN = [
    r"\*\*[^*]+\*\*",  # Bold
    r"\*[^*]+\*",       # Italic
    r"#{1,6}\s+.+",     # Headings
    r"\[.+\]\(https?://[^\)]+\)",  # Links (https only)
    r"^-\s+.+",         # Lists
    r"^\d+\.\s+.+",     # Numbered lists
]


def validate_content(content: str) -> tuple[bool, Optional[str]]:
    """
    Validate generated content for security issues.

    Args:
        content: The generated markdown content

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not content or not content.strip():
        return False, "Content is empty"

    # Check for dangerous patterns
    for pattern in COMPILED_PATTERNS:
        if pattern.search(content):
            return False, f"Dangerous pattern detected: {pattern.pattern}"

    # Check for non-HTTPS URLs
    url_pattern = re.compile(r'http://[^\s\)]+', re.IGNORECASE)
    if url_pattern.search(content):
        return False, "Non-HTTPS URL detected"

    # Check for raw HTML tags (except allowed markdown)
    html_tag_pattern = re.compile(r'<[a-zA-Z][^>]*>')
    if html_tag_pattern.search(content):
        return False, "HTML tags detected in content"

    return True, None


def sanitize_content(content: str) -> str:
    """
    Sanitize content by removing any dangerous elements.
    Use as a fallback if validation fails but content is needed.

    Args:
        content: The content to sanitize

    Returns:
        Sanitized content
    """
    if not content:
        return ""

    result = content

    # Remove dangerous patterns
    for pattern in COMPILED_PATTERNS:
        result = pattern.sub("", result)

    # Remove HTML tags
    result = re.sub(r'<[^>]+>', '', result)

    # Convert http:// to https:// for URLs
    result = re.sub(r'http://', 'https://', result, flags=re.IGNORECASE)

    return result.strip()


def validate_url(url: str) -> bool:
    """
    Validate that a URL is safe to include.

    Args:
        url: The URL to validate

    Returns:
        True if URL is safe
    """
    if not url:
        return False

    # Must be HTTPS
    if not url.startswith("https://"):
        return False

    # No javascript: or data: schemes embedded
    if "javascript:" in url.lower() or "data:" in url.lower():
        return False

    return True
