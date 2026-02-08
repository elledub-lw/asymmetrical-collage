from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, List
import uuid
import json
import time

from ..models import (
    Draft, DraftCreate, DraftUpdate, DraftBatch,
    BatchSubmission, APIResponse, PublishResult
)
from .. import database as db
from ..config import get_settings, Settings
from ..github import publish_to_github

router = APIRouter(prefix="/api/drafts", tags=["drafts"])


def verify_api_key(x_api_key: str = Header(...)) -> bool:
    settings = get_settings()
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


def parse_draft_row(row: dict) -> Draft:
    """Parse a database row into a Draft model."""
    tags = None
    if row.get("tags"):
        try:
            tags = json.loads(row["tags"])
        except json.JSONDecodeError:
            tags = []

    return Draft(
        id=row["id"],
        content=row["content"],
        title=row.get("title"),
        summary=row.get("summary"),
        tags=tags,
        style_type=row.get("style_type"),
        prompt_version=row.get("prompt_version"),
        batch_id=row["batch_id"],
        status=row["status"],
        edited_content=row.get("edited_content"),
        generated_at=row["generated_at"],
        published_at=row.get("published_at"),
        github_commit_sha=row.get("github_commit_sha"),
    )


@router.post("/batch", response_model=APIResponse)
async def receive_batch(submission: BatchSubmission, _: bool = Depends(verify_api_key)):
    """Receive a batch of drafts from GitHub Actions."""
    batch_id = str(uuid.uuid4())
    generated_at = int(time.time())

    for draft in submission.drafts:
        draft_id = str(uuid.uuid4())
        tags_json = json.dumps(draft.tags) if draft.tags else None

        await db.execute(
            """
            INSERT INTO drafts (id, content, title, summary, tags, style_type,
                               prompt_version, batch_id, status, generated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
            """,
            (
                draft_id,
                draft.content,
                draft.title,
                draft.summary,
                tags_json,
                draft.style_type,
                submission.prompt_version or draft.prompt_version,
                batch_id,
                generated_at,
            ),
        )

    return APIResponse(
        success=True,
        message=f"Received {len(submission.drafts)} drafts",
        data={"batch_id": batch_id},
    )


@router.get("/pending", response_model=List[DraftBatch])
async def get_pending_drafts():
    """Get all pending drafts grouped by batch."""
    rows = await db.fetch_all(
        """
        SELECT * FROM drafts
        WHERE status = 'pending'
        ORDER BY generated_at DESC, id
        """
    )

    batches: dict[str, DraftBatch] = {}
    for row in rows:
        draft = parse_draft_row(row)
        if draft.batch_id not in batches:
            batches[draft.batch_id] = DraftBatch(
                batch_id=draft.batch_id,
                generated_at=draft.generated_at,
                drafts=[],
            )
        batches[draft.batch_id].drafts.append(draft)

    return list(batches.values())


@router.get("/{draft_id}", response_model=Draft)
async def get_draft(draft_id: str):
    """Get a single draft by ID."""
    row = await db.fetch_one("SELECT * FROM drafts WHERE id = ?", (draft_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Draft not found")
    return parse_draft_row(row)


@router.put("/{draft_id}", response_model=Draft)
async def update_draft(draft_id: str, update: DraftUpdate):
    """Update a draft."""
    row = await db.fetch_one("SELECT * FROM drafts WHERE id = ?", (draft_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Draft not found")

    updates = []
    params = []

    if update.content is not None:
        updates.append("content = ?")
        params.append(update.content)
    if update.title is not None:
        updates.append("title = ?")
        params.append(update.title)
    if update.summary is not None:
        updates.append("summary = ?")
        params.append(update.summary)
    if update.tags is not None:
        updates.append("tags = ?")
        params.append(json.dumps(update.tags))
    if update.edited_content is not None:
        updates.append("edited_content = ?")
        params.append(update.edited_content)
        updates.append("status = 'edited'")

    if updates:
        params.append(draft_id)
        await db.execute(
            f"UPDATE drafts SET {', '.join(updates)} WHERE id = ?",
            tuple(params),
        )

    row = await db.fetch_one("SELECT * FROM drafts WHERE id = ?", (draft_id,))
    return parse_draft_row(row)


@router.post("/{draft_id}/publish", response_model=PublishResult)
async def publish_draft(draft_id: str):
    """Publish a draft to GitHub."""
    row = await db.fetch_one("SELECT * FROM drafts WHERE id = ?", (draft_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Draft not found")

    draft = parse_draft_row(row)

    # Use edited content if available, otherwise original
    content = draft.edited_content or draft.content
    title = draft.title or "Untitled Post"

    result = await publish_to_github(
        title=title,
        content=content,
        summary=draft.summary,
        tags=draft.tags,
    )

    if result.success:
        published_at = int(time.time())
        await db.execute(
            """
            UPDATE drafts
            SET status = 'published', published_at = ?, github_commit_sha = ?
            WHERE id = ?
            """,
            (published_at, result.commit_sha, draft_id),
        )

        # Also add to published_posts table
        slug = result.github_url.split("/")[-1].replace(".md", "") if result.github_url else ""
        await db.execute(
            """
            INSERT INTO published_posts (id, title, slug, content, published_at,
                                         prompt_version, github_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                title,
                slug,
                content,
                published_at,
                draft.prompt_version,
                result.github_url,
            ),
        )

    return result


@router.post("/{draft_id}/reject", response_model=APIResponse)
async def reject_draft(draft_id: str):
    """Mark a draft as rejected."""
    row = await db.fetch_one("SELECT * FROM drafts WHERE id = ?", (draft_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Draft not found")

    await db.execute(
        "UPDATE drafts SET status = 'rejected' WHERE id = ?",
        (draft_id,),
    )

    return APIResponse(success=True, message="Draft rejected")


@router.get("/", response_model=List[Draft])
async def list_drafts(status: Optional[str] = None, limit: int = 50):
    """List drafts with optional status filter."""
    if status:
        rows = await db.fetch_all(
            "SELECT * FROM drafts WHERE status = ? ORDER BY generated_at DESC LIMIT ?",
            (status, limit),
        )
    else:
        rows = await db.fetch_all(
            "SELECT * FROM drafts ORDER BY generated_at DESC LIMIT ?",
            (limit,),
        )

    return [parse_draft_row(row) for row in rows]
