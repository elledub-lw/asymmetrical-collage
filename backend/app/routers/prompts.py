from fastapi import APIRouter, HTTPException
from typing import Optional, List
import time
import json

from ..models import PromptVersion, PromptVersionCreate, APIResponse
from .. import database as db

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


def parse_prompt_row(row: dict) -> PromptVersion:
    """Parse a database row into a PromptVersion model."""
    return PromptVersion(
        version=row["version"],
        instructions=row["instructions"],
        context=row.get("context"),
        notes=row.get("notes"),
        is_active=bool(row.get("is_active", 0)),
        created_at=row["created_at"],
    )


@router.get("/active", response_model=Optional[PromptVersion])
async def get_active_prompt():
    """Get the currently active prompt version."""
    row = await db.fetch_one(
        "SELECT * FROM prompt_versions WHERE is_active = 1"
    )
    if not row:
        return None
    return parse_prompt_row(row)


@router.get("/", response_model=List[PromptVersion])
async def list_prompts():
    """List all prompt versions."""
    rows = await db.fetch_all(
        "SELECT * FROM prompt_versions ORDER BY created_at DESC"
    )
    return [parse_prompt_row(row) for row in rows]


@router.post("/", response_model=PromptVersion)
async def create_prompt(prompt: PromptVersionCreate):
    """Create a new prompt version."""
    existing = await db.fetch_one(
        "SELECT * FROM prompt_versions WHERE version = ?",
        (prompt.version,),
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Version '{prompt.version}' already exists",
        )

    created_at = int(time.time())
    await db.execute(
        """
        INSERT INTO prompt_versions (version, instructions, context, notes, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (prompt.version, prompt.instructions, prompt.context, prompt.notes, created_at),
    )

    row = await db.fetch_one(
        "SELECT * FROM prompt_versions WHERE version = ?",
        (prompt.version,),
    )
    return parse_prompt_row(row)


@router.get("/{version}", response_model=PromptVersion)
async def get_prompt(version: str):
    """Get a specific prompt version."""
    row = await db.fetch_one(
        "SELECT * FROM prompt_versions WHERE version = ?",
        (version,),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Prompt version not found")
    return parse_prompt_row(row)


@router.post("/{version}/activate", response_model=APIResponse)
async def activate_prompt(version: str):
    """Set a prompt version as active."""
    row = await db.fetch_one(
        "SELECT * FROM prompt_versions WHERE version = ?",
        (version,),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Prompt version not found")

    # Deactivate all other versions
    await db.execute("UPDATE prompt_versions SET is_active = 0")

    # Activate this version
    await db.execute(
        "UPDATE prompt_versions SET is_active = 1 WHERE version = ?",
        (version,),
    )

    return APIResponse(
        success=True,
        message=f"Prompt version '{version}' is now active",
    )


@router.delete("/{version}", response_model=APIResponse)
async def delete_prompt(version: str):
    """Delete a prompt version."""
    row = await db.fetch_one(
        "SELECT * FROM prompt_versions WHERE version = ?",
        (version,),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Prompt version not found")

    if row.get("is_active"):
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the active prompt version",
        )

    await db.execute(
        "DELETE FROM prompt_versions WHERE version = ?",
        (version,),
    )

    return APIResponse(success=True, message=f"Prompt version '{version}' deleted")
