"""
Main orchestration for Market Watch newsletter generation.
Coordinates news gathering, synthesis, storage, and delivery.
"""

import json
import uuid
from datetime import datetime
from typing import Optional

from .time_window import get_time_window, is_weekend
from .sources import get_all_queries
from .prompts import get_perplexity_system_prompt
from .perplexity import gather_news
from .synthesize import synthesize_digest, categorize_digest
from .email import send_digest_email


async def generate_daily_digest(
    db,
    perplexity_key: str,
    anthropic_key: str,
    resend_key: Optional[str] = None,
    to_email: Optional[str] = None,
    from_email: Optional[str] = None,
) -> dict:
    """
    Generate the daily Market Watch digest.

    This is the main entry point for digest generation.
    Handles the full pipeline: news gathering → synthesis → storage → email.

    Args:
        db: Database connection
        perplexity_key: Perplexity API key
        anthropic_key: Anthropic API key
        resend_key: Optional Resend API key for email delivery
        to_email: Optional recipient email
        from_email: Optional sender email

    Returns:
        dict with status, digest_id, and any error messages
    """
    # Check if weekend
    if is_weekend():
        return {
            "status": "skipped",
            "reason": "Weekend - no digest generated",
        }

    # Get time window
    time_window = get_time_window()
    date_iso = time_window["dateISO"]
    today_str = time_window["todayStr"]
    start_iso = time_window["startISO"]
    end_iso = time_window["endISO"]

    # Check if digest already exists for today
    existing = await db.execute(
        "SELECT id, status FROM daily_digests WHERE date_iso = ?",
        (date_iso,)
    )
    row = await existing.fetchone()
    if row:
        return {
            "status": "exists",
            "digest_id": row[0],
            "existing_status": row[1],
            "message": f"Digest already exists for {date_iso}",
        }

    # Create digest record
    digest_id = str(uuid.uuid4())
    now_ts = int(datetime.utcnow().timestamp())

    await db.execute(
        """INSERT INTO daily_digests (id, date_iso, status, created_at, updated_at)
           VALUES (?, ?, 'generating', ?, ?)""",
        (digest_id, date_iso, now_ts, now_ts)
    )
    await db.commit()

    try:
        # Step 1: Gather news from Perplexity
        queries = get_all_queries()
        system_prompt = get_perplexity_system_prompt(start_iso, end_iso)

        news_content, sources = await gather_news(
            queries,
            system_prompt,
            perplexity_key,
        )

        # Step 2: Synthesize digest with Claude
        digest_content, synthesis_error = await synthesize_digest(
            news_content,
            today_str,
            start_iso,
            end_iso,
            anthropic_key,
        )

        if synthesis_error:
            await _update_digest_status(db, digest_id, "failed", error=synthesis_error)
            return {
                "status": "failed",
                "digest_id": digest_id,
                "error": synthesis_error,
            }

        # Step 3: Categorize the digest
        categories = await categorize_digest(digest_content, anthropic_key)

        # Step 4: Store the digest
        now_ts = int(datetime.utcnow().timestamp())
        await db.execute(
            """UPDATE daily_digests
               SET status = 'draft',
                   content = ?,
                   sources_json = ?,
                   categories = ?,
                   updated_at = ?
               WHERE id = ?""",
            (
                digest_content,
                json.dumps(sources),
                json.dumps(categories),
                now_ts,
                digest_id,
            )
        )
        await db.commit()

        # Step 5: Send email if configured
        email_sent = False
        email_error = None
        if resend_key and to_email and from_email:
            email_sent, email_error = await send_digest_email(
                digest_content,
                today_str,
                to_email,
                from_email,
                resend_key,
            )

            if email_sent:
                await _update_digest_status(db, digest_id, "published")

        return {
            "status": "success",
            "digest_id": digest_id,
            "date_iso": date_iso,
            "categories": categories,
            "email_sent": email_sent,
            "email_error": email_error,
        }

    except Exception as e:
        await _update_digest_status(db, digest_id, "failed", error=str(e))
        return {
            "status": "failed",
            "digest_id": digest_id,
            "error": str(e),
        }


async def _update_digest_status(
    db,
    digest_id: str,
    status: str,
    error: Optional[str] = None
):
    """Update digest status in database."""
    now_ts = int(datetime.utcnow().timestamp())
    if error:
        await db.execute(
            """UPDATE daily_digests
               SET status = ?, error_message = ?, updated_at = ?
               WHERE id = ?""",
            (status, error, now_ts, digest_id)
        )
    else:
        await db.execute(
            """UPDATE daily_digests
               SET status = ?, updated_at = ?
               WHERE id = ?""",
            (status, now_ts, digest_id)
        )
    await db.commit()


async def get_digest_by_date(db, date_iso: str) -> Optional[dict]:
    """
    Retrieve a digest by date.

    Args:
        db: Database connection
        date_iso: Date in YYYY-MM-DD format

    Returns:
        Digest dict or None
    """
    result = await db.execute(
        """SELECT id, date_iso, status, content, sources_json, categories,
                  error_message, created_at, updated_at
           FROM daily_digests WHERE date_iso = ?""",
        (date_iso,)
    )
    row = await result.fetchone()

    if not row:
        return None

    return {
        "id": row[0],
        "date_iso": row[1],
        "status": row[2],
        "content": row[3],
        "sources": json.loads(row[4]) if row[4] else [],
        "categories": json.loads(row[5]) if row[5] else [],
        "error_message": row[6],
        "created_at": row[7],
        "updated_at": row[8],
    }


async def get_latest_digest(db) -> Optional[dict]:
    """
    Retrieve the most recent digest.

    Args:
        db: Database connection

    Returns:
        Digest dict or None
    """
    result = await db.execute(
        """SELECT id, date_iso, status, content, sources_json, categories,
                  error_message, created_at, updated_at
           FROM daily_digests
           ORDER BY date_iso DESC
           LIMIT 1"""
    )
    row = await result.fetchone()

    if not row:
        return None

    return {
        "id": row[0],
        "date_iso": row[1],
        "status": row[2],
        "content": row[3],
        "sources": json.loads(row[4]) if row[4] else [],
        "categories": json.loads(row[5]) if row[5] else [],
        "error_message": row[6],
        "created_at": row[7],
        "updated_at": row[8],
    }


async def list_digests(db, limit: int = 30) -> list[dict]:
    """
    List recent digests.

    Args:
        db: Database connection
        limit: Maximum number of digests to return

    Returns:
        List of digest summary dicts
    """
    result = await db.execute(
        """SELECT id, date_iso, status, categories, created_at
           FROM daily_digests
           ORDER BY date_iso DESC
           LIMIT ?""",
        (limit,)
    )
    rows = await result.fetchall()

    return [
        {
            "id": row[0],
            "date_iso": row[1],
            "status": row[2],
            "categories": json.loads(row[3]) if row[3] else [],
            "created_at": row[4],
        }
        for row in rows
    ]
