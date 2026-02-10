#!/usr/bin/env python3
"""
Weekly Feedback Analysis for Asymmetrical Collage

Fetches feedback data from the backend, analyzes patterns with Claude,
and emails suggested framework improvements.
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path
import anthropic
import httpx


def fetch_feedback_data(backend_url: str, api_key: str) -> dict:
    """Fetch rejected, banked, and published drafts from the backend."""
    headers = {"X-API-Key": api_key}

    with httpx.Client(timeout=30.0) as client:
        # Get all drafts
        response = client.get(
            f"{backend_url.rstrip('/')}/api/drafts/",
            headers=headers,
            params={"limit": 100}
        )

        if response.status_code != 200:
            raise Exception(f"Failed to fetch drafts: {response.status_code}")

        drafts = response.json()

    # Filter by status and recency (last 7 days)
    week_ago = datetime.now().timestamp() - (7 * 24 * 60 * 60)

    rejected = []
    banked = []
    published = []

    for draft in drafts:
        generated_at = draft.get("generated_at", 0)

        # Include all rejected/banked regardless of date, but only recent published
        if draft["status"] == "rejected":
            rejected.append({
                "title": draft.get("title") or "Untitled",
                "reason": draft.get("rejection_reason"),
                "content_preview": (draft.get("content") or "")[:300],
                "generated_at": generated_at,
            })
        elif draft["status"] == "banked":
            banked.append({
                "title": draft.get("title") or "Untitled",
                "notes": draft.get("edit_notes"),
                "content_preview": (draft.get("content") or "")[:300],
                "generated_at": generated_at,
            })
        elif draft["status"] == "published" and generated_at > week_ago:
            published.append({
                "title": draft.get("title") or "Untitled",
                "voice_score": draft.get("voice_score"),
                "edit_notes": draft.get("edit_notes"),
                "published_without_edits": draft.get("published_without_edits", False),
                "generated_at": generated_at,
            })

    return {
        "rejected": rejected,
        "banked": banked,
        "published": published,
        "period": {
            "start": datetime.fromtimestamp(week_ago).strftime("%Y-%m-%d"),
            "end": datetime.now().strftime("%Y-%m-%d"),
        }
    }


def read_current_context(repo_root: Path) -> dict:
    """Read current context files for reference."""
    context_dir = repo_root / "context"
    context_files = {}

    for filepath in context_dir.glob("*.md"):
        # Only read key files, skip large ones
        if filepath.name in ["instructions.md", "philosophy.md", "themes.md"]:
            content = filepath.read_text(encoding="utf-8")
            # Truncate to avoid token limits
            context_files[filepath.name] = content[:3000] + "..." if len(content) > 3000 else content

    return context_files


def analyze_feedback(feedback_data: dict, context_files: dict) -> str:
    """Use Claude to analyze feedback and suggest improvements."""
    client = anthropic.Anthropic()

    # Build the analysis prompt
    rejected_summary = "\n\n".join([
        f"**{r['title']}**\nReason: {r['reason'] or 'No reason provided'}\nPreview: {r['content_preview'][:200]}..."
        for r in feedback_data["rejected"]
    ]) or "No rejected drafts this period."

    banked_summary = "\n\n".join([
        f"**{b['title']}**\nNotes: {b['notes'] or 'No notes'}\nPreview: {b['content_preview'][:200]}..."
        for b in feedback_data["banked"]
    ]) or "No banked drafts this period."

    published_summary = "\n\n".join([
        f"**{p['title']}**\nVoice Score: {p['voice_score'] or 'Not rated'}\nEdit Notes: {p['edit_notes'] or 'None'}\nPublished without edits: {p['published_without_edits']}"
        for p in feedback_data["published"]
    ]) or "No published drafts this period."

    prompt = f"""You are analyzing feedback from a daily blog generation system to suggest improvements.

## Period: {feedback_data['period']['start']} to {feedback_data['period']['end']}

## Rejected Drafts (with reasons)
{rejected_summary}

## Banked Drafts (saved for later)
{banked_summary}

## Published Drafts (with feedback)
{published_summary}

## Current Context Files (excerpts)

### instructions.md
{context_files.get('instructions.md', 'Not available')[:2000]}

### philosophy.md
{context_files.get('philosophy.md', 'Not available')[:1500]}

---

## Your Task

Analyze the feedback patterns and suggest specific improvements to the framework. Structure your response as:

### 1. Rejection Pattern Analysis
- What themes/approaches keep getting rejected?
- What specific issues are mentioned repeatedly?
- Any new patterns that should be added to "Flagged Examples"?

### 2. Voice Score Analysis
- What worked well in high-scoring drafts?
- What patterns appear in low-scoring drafts?
- Any refinements needed to voice guidance?

### 3. Banked Draft Observations
- What kinds of drafts are being saved for later?
- Are there patterns in why drafts get banked vs. rejected?
- Any that seem ready to publish with minor tweaks?

### 4. Suggested Framework Updates

For each suggestion, provide:
- **File to update:** (e.g., instructions.md, philosophy.md, themes.md)
- **Section:** (specific section name)
- **Current state:** (brief description)
- **Proposed change:** (specific text or guidance to add/modify)
- **Rationale:** (why this improvement matters)

### 5. Theme Cooldowns to Add/Remove
- Any themes that should be added to cooldown?
- Any cooldowns that should be lifted?

### 6. Summary
- Top 3 most impactful changes to make
- Overall system health assessment
- Any concerns or patterns to watch

Be specific and actionable. The goal is to give Laurent clear recommendations he can approve or reject."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text


def send_email(analysis: str, feedback_data: dict, recipient: str, sender: str, password: str):
    """Send the analysis via Gmail SMTP."""
    today = datetime.now().strftime("%B %d, %Y")
    period = f"{feedback_data['period']['start']} to {feedback_data['period']['end']}"

    # Stats
    rejected_count = len(feedback_data["rejected"])
    banked_count = len(feedback_data["banked"])
    published_count = len(feedback_data["published"])

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Weekly Blog Feedback Analysis - {today}"
    msg["From"] = sender
    msg["To"] = recipient

    text_content = f"""Weekly Blog Feedback Analysis
Period: {period}

Stats:
- Rejected: {rejected_count}
- Banked: {banked_count}
- Published (this week): {published_count}

---

{analysis}

---
Generated by your weekly feedback analysis automation.
"""

    # Simple HTML version
    html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #333;">

<div style="background: #1e293b; padding: 20px 25px; border-radius: 8px; margin-bottom: 30px;">
    <h1 style="color: white; font-size: 24px; margin: 0 0 5px 0;">Weekly Blog Feedback Analysis</h1>
    <p style="color: #94a3b8; font-size: 14px; margin: 0;">Period: {period}</p>
</div>

<div style="display: flex; gap: 20px; margin-bottom: 30px;">
    <div style="flex: 1; padding: 15px; background: #fef2f2; border-radius: 8px; text-align: center;">
        <div style="font-size: 32px; font-weight: bold; color: #dc2626;">{rejected_count}</div>
        <div style="color: #991b1b;">Rejected</div>
    </div>
    <div style="flex: 1; padding: 15px; background: #fffbeb; border-radius: 8px; text-align: center;">
        <div style="font-size: 32px; font-weight: bold; color: #d97706;">{banked_count}</div>
        <div style="color: #92400e;">Banked</div>
    </div>
    <div style="flex: 1; padding: 15px; background: #f0fdf4; border-radius: 8px; text-align: center;">
        <div style="font-size: 32px; font-weight: bold; color: #16a34a;">{published_count}</div>
        <div style="color: #166534;">Published</div>
    </div>
</div>

<div style="line-height: 1.6; white-space: pre-wrap;">{analysis}</div>

<div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd;">
    <p style="color: #888; font-size: 14px; margin: 0;">Generated by your weekly feedback analysis automation.</p>
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

    print(f"Analysis email sent to {recipient}")


def main():
    # Get environment variables
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    backend_url = os.environ.get("SYNOLOGY_URL")
    backend_api_key = os.environ.get("SYNOLOGY_API_KEY")
    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")

    if not all([anthropic_key, backend_url, backend_api_key, gmail_address, gmail_password]):
        raise ValueError("Missing required environment variables")

    # Set up paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    print("Fetching feedback data from backend...")
    feedback_data = fetch_feedback_data(backend_url, backend_api_key)
    print(f"Found: {len(feedback_data['rejected'])} rejected, {len(feedback_data['banked'])} banked, {len(feedback_data['published'])} published")

    # Check if there's any feedback to analyze
    total_feedback = len(feedback_data["rejected"]) + len(feedback_data["banked"]) + len(feedback_data["published"])
    if total_feedback == 0:
        print("No feedback data to analyze. Skipping.")
        return

    print("Reading current context files...")
    context_files = read_current_context(repo_root)
    print(f"Loaded {len(context_files)} context files")

    print("Analyzing feedback with Claude...")
    analysis = analyze_feedback(feedback_data, context_files)
    print("Analysis complete")

    print("Sending email...")
    send_email(analysis, feedback_data, gmail_address, gmail_address, gmail_password)

    print("Done!")


if __name__ == "__main__":
    main()
