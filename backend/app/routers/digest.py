"""
API routes for Market Watch newsletter digest.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from ..config import get_settings
from ..database import get_db

settings = get_settings()
from ..digest.generator import (
    generate_daily_digest,
    get_digest_by_date,
    get_latest_digest,
    list_digests,
)
from ..digest.time_window import get_today_iso, is_weekend


router = APIRouter(prefix="/api/digest", tags=["digest"])


# Job lock state ID
JOB_LOCK_ID = "00000000-0000-0000-0000-000000000001"


class GenerateResponse(BaseModel):
    status: str
    digest_id: Optional[str] = None
    date_iso: Optional[str] = None
    categories: Optional[list[str]] = None
    email_sent: Optional[bool] = None
    error: Optional[str] = None
    message: Optional[str] = None


class DigestResponse(BaseModel):
    id: str
    date_iso: str
    status: str
    content: Optional[str] = None
    sources: list[dict] = []
    categories: list[str] = []
    error_message: Optional[str] = None
    created_at: int
    updated_at: int


class DigestSummary(BaseModel):
    id: str
    date_iso: str
    status: str
    categories: list[str] = []
    created_at: int


def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from header."""
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


async def acquire_job_lock(db) -> bool:
    """
    Try to acquire the job lock for digest generation.
    Returns True if lock acquired, False if already locked.
    """
    now_ts = int(datetime.utcnow().timestamp())

    # Check if lock exists and is held
    result = await db.execute(
        "SELECT is_locked, locked_at FROM digest_job_state WHERE id = ?",
        (JOB_LOCK_ID,)
    )
    row = await result.fetchone()

    if row:
        is_locked, locked_at = row
        # Consider lock stale after 10 minutes
        if is_locked and locked_at and (now_ts - locked_at) < 600:
            return False
        # Update existing lock
        await db.execute(
            """UPDATE digest_job_state
               SET is_locked = 1, locked_at = ?, locked_by = 'api'
               WHERE id = ?""",
            (now_ts, JOB_LOCK_ID)
        )
    else:
        # Create lock record
        await db.execute(
            """INSERT INTO digest_job_state (id, is_locked, locked_at, locked_by)
               VALUES (?, 1, ?, 'api')""",
            (JOB_LOCK_ID, now_ts)
        )

    await db.commit()
    return True


async def release_job_lock(db, status: str):
    """Release the job lock and record run status."""
    now_ts = int(datetime.utcnow().timestamp())
    await db.execute(
        """UPDATE digest_job_state
           SET is_locked = 0, locked_at = NULL, locked_by = NULL,
               last_run_at = ?, last_run_status = ?
           WHERE id = ?""",
        (now_ts, status, JOB_LOCK_ID)
    )
    await db.commit()


@router.post("/generate", response_model=GenerateResponse)
async def trigger_generate(
    _: str = Depends(verify_api_key),
    db=Depends(get_db),
):
    """
    Trigger digest generation for today.
    Called by GitHub Actions daily at 17:00 UTC (18:00 Paris).
    """
    # Skip weekends
    if is_weekend():
        return GenerateResponse(
            status="skipped",
            message="Weekend - no digest generated",
        )

    # Acquire job lock
    if not await acquire_job_lock(db):
        raise HTTPException(
            status_code=409,
            detail="Digest generation already in progress"
        )

    try:
        result = await generate_daily_digest(
            db=db,
            perplexity_key=settings.perplexity_api_key,
            anthropic_key=settings.anthropic_api_key,
            resend_key=getattr(settings, 'resend_api_key', None),
            to_email=getattr(settings, 'digest_to_email', None),
            from_email=getattr(settings, 'digest_from_email', None),
        )

        await release_job_lock(db, result.get("status", "unknown"))

        return GenerateResponse(**result)

    except Exception as e:
        await release_job_lock(db, "error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/today", response_model=Optional[DigestResponse])
async def get_today_digest(db=Depends(get_db)):
    """Get today's digest if it exists."""
    date_iso = get_today_iso()
    digest = await get_digest_by_date(db, date_iso)

    if not digest:
        raise HTTPException(status_code=404, detail="No digest for today")

    return DigestResponse(**digest)


@router.get("/latest", response_model=Optional[DigestResponse])
async def get_latest(db=Depends(get_db)):
    """Get the most recent digest."""
    digest = await get_latest_digest(db)

    if not digest:
        raise HTTPException(status_code=404, detail="No digests found")

    return DigestResponse(**digest)


@router.get("/date/{date_iso}", response_model=DigestResponse)
async def get_by_date(date_iso: str, db=Depends(get_db)):
    """Get digest by date (YYYY-MM-DD format)."""
    digest = await get_digest_by_date(db, date_iso)

    if not digest:
        raise HTTPException(
            status_code=404,
            detail=f"No digest found for {date_iso}"
        )

    return DigestResponse(**digest)


@router.get("/list", response_model=list[DigestSummary])
async def list_all(limit: int = 30, db=Depends(get_db)):
    """List recent digests."""
    digests = await list_digests(db, limit)
    return [DigestSummary(**d) for d in digests]


@router.get("/status")
async def get_status(db=Depends(get_db)):
    """Get the current status of digest generation."""
    # Get job state
    result = await db.execute(
        "SELECT is_locked, locked_at, last_run_at, last_run_status FROM digest_job_state WHERE id = ?",
        (JOB_LOCK_ID,)
    )
    row = await result.fetchone()

    job_state = None
    if row:
        job_state = {
            "is_locked": bool(row[0]),
            "locked_at": row[1],
            "last_run_at": row[2],
            "last_run_status": row[3],
        }

    # Get today's digest status
    date_iso = get_today_iso()
    today_digest = await get_digest_by_date(db, date_iso)

    return {
        "date_iso": date_iso,
        "is_weekend": is_weekend(),
        "job_state": job_state,
        "today_digest": {
            "id": today_digest["id"],
            "status": today_digest["status"],
        } if today_digest else None,
    }
