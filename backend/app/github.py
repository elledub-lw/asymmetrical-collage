import httpx
import base64
import re
from datetime import datetime
from typing import Optional

from .config import get_settings
from .models import PublishResult


def generate_slug(title: str) -> str:
    """Generate a URL-friendly slug from title."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug[:50]


def build_hugo_frontmatter(
    title: str,
    summary: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> str:
    """Build Hugo front matter for blog post."""
    today = datetime.now().strftime("%Y-%m-%d")

    frontmatter = f'''---
title: "{title}"
date: {today}
draft: false
'''

    if tags:
        tags_str = ", ".join(f'"{tag}"' for tag in tags)
        frontmatter += f"tags: [{tags_str}]\n"

    if summary:
        frontmatter += f'summary: "{summary}"\n'

    frontmatter += 'image: ""\n---\n\n'

    return frontmatter


async def publish_to_github(
    title: str,
    content: str,
    summary: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> PublishResult:
    """Publish a blog post to GitHub via Contents API."""
    settings = get_settings()

    slug = generate_slug(title)
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"{today}-{slug}.md"
    path = f"content/articles/{filename}"

    frontmatter = build_hugo_frontmatter(title, summary, tags)
    full_content = frontmatter + content

    # Encode content as base64
    content_bytes = full_content.encode("utf-8")
    content_base64 = base64.b64encode(content_bytes).decode("utf-8")

    # GitHub API request
    url = f"https://api.github.com/repos/{settings.github_repo}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {settings.github_token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    payload = {
        "message": f"Add blog post: {title}",
        "content": content_base64,
        "branch": "main",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=payload, headers=headers)

            if response.status_code in (200, 201):
                data = response.json()
                commit_sha = data.get("commit", {}).get("sha")
                github_url = data.get("content", {}).get("html_url")

                return PublishResult(
                    success=True,
                    github_url=github_url,
                    commit_sha=commit_sha,
                )
            else:
                error_msg = response.json().get("message", response.text)
                return PublishResult(
                    success=False,
                    error=f"GitHub API error: {error_msg}",
                )

    except httpx.HTTPError as e:
        return PublishResult(
            success=False,
            error=f"HTTP error: {str(e)}",
        )
    except Exception as e:
        return PublishResult(
            success=False,
            error=f"Unexpected error: {str(e)}",
        )
