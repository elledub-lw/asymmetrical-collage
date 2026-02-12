"""
Email delivery for Market Watch newsletter using Resend API.
"""

import httpx
from typing import Optional
import re


RESEND_API_URL = "https://api.resend.com/emails"


def markdown_to_html(markdown: str) -> str:
    """
    Convert markdown to basic HTML for email rendering.
    Simple conversion for newsletter formatting.

    Args:
        markdown: Markdown content

    Returns:
        HTML content
    """
    if not markdown:
        return ""

    html = markdown

    # Convert headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Convert bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

    # Convert italic
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Convert links
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)

    # Convert line breaks to paragraphs
    paragraphs = html.split('\n\n')
    html = '\n'.join(f'<p>{p}</p>' if not p.startswith('<h') and not p.startswith('<p') else p
                     for p in paragraphs if p.strip())

    # Convert single line breaks within paragraphs
    html = html.replace('\n', '<br>')

    return html


def build_email_html(content: str, date_str: str) -> str:
    """
    Build the full HTML email with styling.

    Args:
        content: Markdown content of the digest
        date_str: Formatted date string

    Returns:
        Complete HTML email
    """
    body_html = markdown_to_html(content)

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market Watch - {date_str}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            max-width: 680px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: #ffffff;
            padding: 32px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a1a1a;
            font-size: 28px;
            margin-bottom: 8px;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 12px;
        }}
        h2 {{
            color: #374151;
            font-size: 20px;
            margin-top: 28px;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #e5e7eb;
        }}
        h3 {{
            color: #4b5563;
            font-size: 16px;
            margin-top: 20px;
        }}
        p {{
            margin: 12px 0;
            color: #374151;
        }}
        a {{
            color: #2563eb;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        strong {{
            color: #1a1a1a;
        }}
        .header {{
            text-align: center;
            margin-bottom: 24px;
        }}
        .date {{
            color: #6b7280;
            font-size: 14px;
            margin-top: 4px;
        }}
        .footer {{
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
            font-size: 12px;
            color: #9ca3af;
            text-align: center;
        }}
        hr {{
            border: none;
            border-top: 1px solid #e5e7eb;
            margin: 24px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Market Watch</h1>
            <div class="date">{date_str}</div>
        </div>

        {body_html}

        <div class="footer">
            <p>Market Watch by Asymmetrical Collage</p>
            <p>Bitcoin • Open Source • Fintech • Regulatory • Privacy • AI</p>
        </div>
    </div>
</body>
</html>"""


async def send_digest_email(
    content: str,
    date_str: str,
    to_email: str,
    from_email: str,
    api_key: str,
) -> tuple[bool, Optional[str]]:
    """
    Send the digest via Resend API.

    Args:
        content: Markdown content of the digest
        date_str: Formatted date string
        to_email: Recipient email address
        from_email: Sender email address (must be verified in Resend)
        api_key: Resend API key

    Returns:
        Tuple of (success, error_message)
    """
    html_content = build_email_html(content, date_str)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "from": from_email,
        "to": [to_email],
        "subject": f"Market Watch - {date_str}",
        "html": html_content,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                RESEND_API_URL,
                headers=headers,
                json=payload,
            )

            if response.status_code == 200:
                return True, None
            else:
                error_text = response.text
                print(f"Resend API error: {response.status_code} - {error_text}")
                return False, f"Email send failed: {response.status_code}"

        except httpx.TimeoutException:
            return False, "Email send timed out"
        except Exception as e:
            return False, f"Email send error: {str(e)}"
