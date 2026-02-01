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

    # Order matters - instructions first
    priority_order = ['instructions', 'themes', 'writing_styles', 'refinements', 'banked_drafts', 'exemplar_posts']

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
    """Convert markdown to HTML with proper formatting."""
    html = text

    # Convert headers
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)

    # Convert bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Convert italic
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Convert line breaks (but not inside tags)
    html = re.sub(r'\n\n', '</p><p>', html)
    html = re.sub(r'\n', '<br>', html)

    # Wrap in paragraph
    html = f'<p>{html}</p>'

    # Clean up empty paragraphs
    html = re.sub(r'<p>\s*</p>', '', html)
    html = re.sub(r'<p>\s*<h', '<h', html)
    html = re.sub(r'</h(\d)>\s*</p>', r'</h\1>', html)

    return html


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
<style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 700px;
        margin: 0 auto;
        padding: 20px;
        font-size: 16px;
    }}
    h1 {{
        color: #05445E;
        border-bottom: 2px solid #189AB4;
        padding-bottom: 10px;
        font-size: 24px;
        margin-top: 0;
    }}
    h2 {{
        color: #189AB4;
        margin-top: 30px;
        margin-bottom: 15px;
        font-size: 20px;
        border-left: 4px solid #189AB4;
        padding-left: 12px;
    }}
    h3 {{
        color: #05445E;
        font-size: 16px;
        margin-top: 20px;
    }}
    p {{
        margin: 10px 0;
        font-size: 16px;
    }}
    strong {{
        color: #05445E;
    }}
    .header {{
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 30px;
    }}
    .header h1 {{
        margin: 0;
        border: none;
        padding: 0;
    }}
    .header p {{
        margin: 10px 0 0 0;
        color: #666;
    }}
    hr {{
        border: none;
        border-top: 1px solid #ddd;
        margin: 30px 0;
    }}
    .footer {{
        color: #888;
        font-size: 14px;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #eee;
    }}
</style>
</head>
<body>
<div class="header">
    <h1>Daily Blog Ideas</h1>
    <p>Generated on {today} for Asymmetrical Collage</p>
</div>

{ideas_html}

<div class="footer">
    <p>Generated by your daily blog idea automation.</p>
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

    if not all([api_key, gmail_address, gmail_password]):
        raise ValueError("Missing required environment variables: ANTHROPIC_API_KEY, GMAIL_ADDRESS, GMAIL_APP_PASSWORD")

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

    print("Sending email...")
    send_email(ideas, gmail_address, gmail_address, gmail_password)

    print("Done!")


if __name__ == "__main__":
    main()
