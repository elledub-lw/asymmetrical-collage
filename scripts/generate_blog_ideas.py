#!/usr/bin/env python3
"""
Daily Blog Idea Generator for Asymmetrical Collage

Reads recent blog posts and context files, uses Claude API to generate 3 new post ideas,
and sends them via Gmail.
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
import anthropic
import re
import json
import httpx


def get_recent_posts(articles_dir: Path, count: int = 10) -> list[dict]:
    """Read the most recent blog posts."""
    posts = []

    for filepath in sorted(articles_dir.glob("*.md"), reverse=True):
        if filepath.name.startswith("_"):
            continue

        content = filepath.read_text(encoding="utf-8")

        # Parse front matter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                front_matter = parts[1].strip()
                body = parts[2].strip()

                # Extract title and summary from front matter
                title = ""
                summary = ""
                tags = ""
                for line in front_matter.split("\n"):
                    if line.startswith("title:"):
                        title = line.replace("title:", "").strip().strip('"')
                    elif line.startswith("summary:"):
                        summary = line.replace("summary:", "").strip().strip('"')
                    elif line.startswith("tags:"):
                        tags = line.replace("tags:", "").strip()

                posts.append({
                    "filename": filepath.name,
                    "title": title,
                    "summary": summary,
                    "tags": tags,
                    "body": body[:500]  # First 500 chars of body
                })

        if len(posts) >= count:
            break

    return posts


def read_all_context_files(context_dir: Path) -> dict[str, str]:
    """Read all context files from the context directory."""
    context_files = {}

    if not context_dir.exists():
        return context_files

    for filepath in context_dir.glob("*.md"):
        content = filepath.read_text(encoding="utf-8")
        # Skip files that are just placeholder templates
        if content.strip() and not content.strip().startswith("<!--"):
            context_files[filepath.stem] = content

    return context_files


def generate_ideas(recent_posts: list[dict], context_files: dict[str, str]) -> str:
    """Use Claude API to generate blog post ideas."""
    client = anthropic.Anthropic()

    # Format recent posts for the prompt
    posts_summary = "\n\n".join([
        f"**{p['title']}**\nTags: {p['tags']}\nSummary: {p['summary']}\nExcerpt: {p['body'][:200]}..."
        for p in recent_posts[:10]
    ])

    # Build context from all files
    context_sections = []

    # Order matters - philosophy and instructions first
    priority_order = ['philosophy', 'instructions', 'themes', 'writing_styles', 'refinements', 'banked_drafts', 'exemplar_posts']

    for key in priority_order:
        if key in context_files:
            context_sections.append(f"## {key.upper().replace('_', ' ')}\n\n{context_files[key]}")

    # Add any remaining files
    for key, content in context_files.items():
        if key not in priority_order:
            context_sections.append(f"## {key.upper().replace('_', ' ')}\n\n{content}")

    full_context = "\n\n---\n\n".join(context_sections)

    prompt = f"""You are a creative writing assistant for the blog "Asymmetrical Collage."

{full_context}

---

## RECENT POSTS (to avoid repetition)

{posts_summary}

---

## YOUR TASK

Based on the instructions and context above, generate 3 unique blog post ideas.

For each idea, provide:
- **Title:** A compelling, concise title (shorter and punchier is better)
- **Summary:** One intriguing sentence for RSS (not an explanation - make the reader want to click)
- **Tags:** 3-4 relevant tags
- **Style:** Which writing style from WRITING_STYLES this uses
- **Hook:** The opening paragraph (2-3 sentences that grab attention)
- **Core Insight:** The main point to develop (1-2 sentences)
- **Closing:** A suggested ending (vary format: question, assertion, directive, or observation)

Format your response clearly with "## Idea 1:", "## Idea 2:", "## Idea 3:" headers.

End with a brief "## My Take:" section explaining why each draft takes its approach and which you think is strongest."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text


def markdown_to_html(text: str) -> str:
    """Convert markdown to HTML with proper formatting for email clients."""
    lines = text.split('\n')
    html_parts = []
    in_paragraph = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_paragraph:
                html_parts.append('</p>')
                in_paragraph = False
            continue

        # Convert ## headers (Idea 1, Idea 2, etc.)
        if stripped.startswith('## '):
            if in_paragraph:
                html_parts.append('</p>')
                in_paragraph = False
            header_text = stripped[3:]
            html_parts.append(f'<h2 style="color: #189AB4; font-size: 20px; margin: 30px 0 15px 0; padding: 10px 15px; background: #f0f7f9; border-left: 4px solid #189AB4; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">{header_text}</h2>')
            continue

        # Convert ### headers
        if stripped.startswith('### '):
            if in_paragraph:
                html_parts.append('</p>')
                in_paragraph = False
            header_text = stripped[4:]
            html_parts.append(f'<h3 style="color: #05445E; font-size: 16px; margin: 20px 0 10px 0; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">{header_text}</h3>')
            continue

        # Convert bold **text**
        stripped = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color: #05445E;">\1</strong>', stripped)

        # Convert italic *text*
        stripped = re.sub(r'\*(.+?)\*', r'<em>\1</em>', stripped)

        # Convert bullet points
        if stripped.startswith('- '):
            if in_paragraph:
                html_parts.append('</p>')
                in_paragraph = False
            bullet_text = stripped[2:]
            html_parts.append(f'<p style="margin: 5px 0 5px 20px; font-size: 16px; line-height: 1.6; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">• {bullet_text}</p>')
            continue

        # Regular paragraph text
        if not in_paragraph:
            html_parts.append('<p style="margin: 10px 0; font-size: 16px; line-height: 1.6; color: #333; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">')
            in_paragraph = True
            html_parts.append(stripped)
        else:
            html_parts.append('<br>' + stripped)

    if in_paragraph:
        html_parts.append('</p>')

    return '\n'.join(html_parts)


def parse_ideas_to_drafts(ideas_text: str) -> list[dict]:
    """Parse Claude's response into structured drafts."""
    drafts = []

    # Split by "## Idea" headers
    idea_pattern = r'## Idea \d+[:\s]*(.*?)(?=## Idea \d+|## My Take|$)'
    matches = re.findall(idea_pattern, ideas_text, re.DOTALL | re.IGNORECASE)

    for match in matches:
        idea_text = match.strip()
        if not idea_text:
            continue

        draft = {
            "content": idea_text,
            "title": None,
            "summary": None,
            "tags": [],
            "style_type": None,
        }

        # Extract title
        title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', idea_text)
        if title_match:
            draft["title"] = title_match.group(1).strip()

        # Extract summary
        summary_match = re.search(r'\*\*Summary:\*\*\s*(.+?)(?:\n|$)', idea_text)
        if summary_match:
            draft["summary"] = summary_match.group(1).strip()

        # Extract tags
        tags_match = re.search(r'\*\*Tags:\*\*\s*(.+?)(?:\n|$)', idea_text)
        if tags_match:
            tags_str = tags_match.group(1).strip()
            # Parse tags from various formats
            tags = re.findall(r'[\w-]+', tags_str)
            draft["tags"] = [t for t in tags if t.lower() not in ['and', 'or', 'the']]

        # Extract style
        style_match = re.search(r'\*\*Style:\*\*\s*(.+?)(?:\n|$)', idea_text)
        if style_match:
            draft["style_type"] = style_match.group(1).strip()

        drafts.append(draft)

    return drafts


def send_to_synology(drafts: list[dict], synology_url: str, api_key: str, prompt_version: str = None) -> bool:
    """Send drafts to Synology backend via API."""
    try:
        payload = {
            "drafts": drafts,
            "prompt_version": prompt_version,
        }

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{synology_url.rstrip('/')}/api/drafts/batch",
                json=payload,
                headers=headers,
            )

            if response.status_code == 200:
                data = response.json()
                print(f"Synology: Received batch {data.get('data', {}).get('batch_id', 'unknown')}")
                return True
            else:
                print(f"Synology API error: {response.status_code} - {response.text}")
                return False

    except Exception as e:
        print(f"Failed to send to Synology: {e}")
        return False


def send_email(ideas: str, recipient: str, sender: str, password: str):
    """Send the ideas via Gmail SMTP."""
    today = datetime.now().strftime("%B %d, %Y")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Daily Blog Ideas - {today}"
    msg["From"] = sender
    msg["To"] = recipient

    # Plain text version
    text_content = f"""Daily Blog Ideas for Asymmetrical Collage
Generated on {today}

{ideas}

---
Generated by your daily blog idea automation.
"""

    # HTML version with proper formatting
    ideas_html = markdown_to_html(ideas)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 700px; margin: 0 auto; padding: 20px;">

<div style="background: #05445E; padding: 20px 25px; border-radius: 8px; margin-bottom: 30px;">
    <h1 style="color: white; font-size: 24px; margin: 0 0 5px 0; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">Daily Blog Ideas</h1>
    <p style="color: #a0d2db; font-size: 14px; margin: 0;">Generated on {today} for Asymmetrical Collage</p>
</div>

{ideas_html}

<div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd;">
    <p style="color: #888; font-size: 14px; margin: 0;">Generated by your daily blog idea automation.</p>
</div>

</body>
</html>
"""

    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    # Send via Gmail SMTP
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print(f"Email sent successfully to {recipient}")


def main():
    # Get environment variables
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")

    # Synology backend (optional - takes priority if configured)
    synology_url = os.environ.get("SYNOLOGY_URL")
    synology_api_key = os.environ.get("SYNOLOGY_API_KEY")

    # Check if at least one delivery method is configured
    has_synology = synology_url and synology_api_key
    has_email = gmail_address and gmail_password

    if not api_key:
        raise ValueError("Missing required environment variable: ANTHROPIC_API_KEY")

    if not has_synology and not has_email:
        raise ValueError("No delivery method configured. Set either SYNOLOGY_URL/SYNOLOGY_API_KEY or GMAIL_ADDRESS/GMAIL_APP_PASSWORD")

    # Set up paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    articles_dir = repo_root / "content" / "articles"
    context_dir = repo_root / "context"

    print("Reading recent blog posts...")
    recent_posts = get_recent_posts(articles_dir)
    print(f"Found {len(recent_posts)} recent posts")

    print("Reading context files...")
    context_files = read_all_context_files(context_dir)
    print(f"Loaded {len(context_files)} context files: {list(context_files.keys())}")

    print("Generating blog ideas with Claude...")
    ideas = generate_ideas(recent_posts, context_files)
    print("Ideas generated successfully")

    # Try Synology first, fall back to email
    sent_to_synology = False
    if has_synology:
        print("Sending to Synology backend...")
        drafts = parse_ideas_to_drafts(ideas)
        print(f"Parsed {len(drafts)} drafts from response")
        sent_to_synology = send_to_synology(drafts, synology_url, synology_api_key)

    # Email as fallback or if Synology not configured
    if has_email and (not has_synology or not sent_to_synology):
        if not sent_to_synology and has_synology:
            print("Synology failed, falling back to email...")
        print("Sending email...")
        send_email(ideas, gmail_address, gmail_address, gmail_password)

    print("Done!")


if __name__ == "__main__":
    main()
