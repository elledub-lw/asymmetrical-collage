from fastapi import APIRouter
from typing import List

from ..models import AnalyticsSummary, PromptVersionStats, PublishedPost
from .. import database as db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/", response_model=AnalyticsSummary)
async def get_analytics():
    """Get analytics summary by prompt version."""
    # Get overall counts
    total_drafts_row = await db.fetch_one("SELECT COUNT(*) as count FROM drafts")
    total_drafts = total_drafts_row["count"] if total_drafts_row else 0

    published_row = await db.fetch_one(
        "SELECT COUNT(*) as count FROM drafts WHERE status = 'published'"
    )
    total_published = published_row["count"] if published_row else 0

    rejected_row = await db.fetch_one(
        "SELECT COUNT(*) as count FROM drafts WHERE status = 'rejected'"
    )
    total_rejected = rejected_row["count"] if rejected_row else 0

    overall_publish_rate = (
        total_published / total_drafts if total_drafts > 0 else 0.0
    )

    # Get stats by prompt version
    version_rows = await db.fetch_all(
        """
        SELECT
            prompt_version,
            COUNT(*) as total,
            SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published,
            SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending
        FROM drafts
        WHERE prompt_version IS NOT NULL
        GROUP BY prompt_version
        ORDER BY prompt_version DESC
        """
    )

    by_version = []
    for row in version_rows:
        total = row["total"]
        published = row["published"]
        publish_rate = published / total if total > 0 else 0.0

        # Get average edit time for this version
        edit_time_row = await db.fetch_one(
            """
            SELECT AVG(edit_time_seconds) as avg_time
            FROM published_posts
            WHERE prompt_version = ? AND edit_time_seconds IS NOT NULL
            """,
            (row["prompt_version"],),
        )
        avg_edit_time = (
            edit_time_row["avg_time"] if edit_time_row and edit_time_row["avg_time"] else None
        )

        by_version.append(
            PromptVersionStats(
                version=row["prompt_version"] or "unknown",
                total_drafts=total,
                published_count=published,
                rejected_count=row["rejected"],
                pending_count=row["pending"],
                publish_rate=publish_rate,
                avg_edit_time_seconds=avg_edit_time,
            )
        )

    return AnalyticsSummary(
        total_drafts=total_drafts,
        total_published=total_published,
        total_rejected=total_rejected,
        overall_publish_rate=overall_publish_rate,
        by_version=by_version,
    )


@router.get("/published", response_model=List[PublishedPost])
async def get_published_posts(limit: int = 50):
    """Get list of published posts."""
    rows = await db.fetch_all(
        """
        SELECT * FROM published_posts
        ORDER BY published_at DESC
        LIMIT ?
        """,
        (limit,),
    )

    return [
        PublishedPost(
            id=row["id"],
            title=row["title"],
            slug=row["slug"],
            content=row["content"],
            published_at=row["published_at"],
            prompt_version=row.get("prompt_version"),
            edit_time_seconds=row.get("edit_time_seconds"),
            github_url=row.get("github_url"),
        )
        for row in rows
    ]
