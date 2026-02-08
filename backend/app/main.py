from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from pathlib import Path
import markdown
import json

from .database import init_db, fetch_all, fetch_one
from .routers import drafts, prompts, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Blog Automation Backend", lifespan=lifespan)

# Mount static files
static_path = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Templates
templates_path = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=templates_path)

# Include API routers
app.include_router(drafts.router)
app.include_router(prompts.router)
app.include_router(analytics.router)


def parse_tags(tags_str: str | None) -> list[str]:
    """Parse JSON tags string to list."""
    if not tags_str:
        return []
    try:
        return json.loads(tags_str)
    except json.JSONDecodeError:
        return []


def format_timestamp(ts: int | None) -> str:
    """Format unix timestamp for display."""
    if not ts:
        return ""
    from datetime import datetime
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


# Add custom filters to templates
templates.env.filters["parse_tags"] = parse_tags
templates.env.filters["format_timestamp"] = format_timestamp
templates.env.filters["markdown"] = lambda text: markdown.markdown(text) if text else ""


# Web UI Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard showing pending drafts."""
    rows = await fetch_all(
        """
        SELECT * FROM drafts
        WHERE status = 'pending'
        ORDER BY generated_at DESC, id
        """
    )

    # Group by batch
    batches: dict = {}
    for row in rows:
        batch_id = row["batch_id"]
        if batch_id not in batches:
            batches[batch_id] = {
                "batch_id": batch_id,
                "generated_at": row["generated_at"],
                "drafts": [],
            }
        batches[batch_id]["drafts"].append(row)

    return templates.TemplateResponse(
        "pages/dashboard.html",
        {"request": request, "batches": list(batches.values())},
    )


@app.get("/review/{draft_id}", response_class=HTMLResponse)
async def review_draft(request: Request, draft_id: str):
    """Review and edit a single draft."""
    draft = await fetch_one("SELECT * FROM drafts WHERE id = ?", (draft_id,))
    if not draft:
        return templates.TemplateResponse(
            "pages/404.html",
            {"request": request, "message": "Draft not found"},
            status_code=404,
        )

    return templates.TemplateResponse(
        "pages/review.html",
        {"request": request, "draft": draft},
    )


@app.get("/prompts", response_class=HTMLResponse)
async def prompts_page(request: Request):
    """Prompt version management page."""
    versions = await fetch_all(
        "SELECT * FROM prompt_versions ORDER BY created_at DESC"
    )

    return templates.TemplateResponse(
        "pages/prompts.html",
        {"request": request, "versions": versions},
    )


@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Analytics dashboard."""
    # Get overall stats
    total_row = await fetch_one("SELECT COUNT(*) as count FROM drafts")
    published_row = await fetch_one(
        "SELECT COUNT(*) as count FROM drafts WHERE status = 'published'"
    )
    rejected_row = await fetch_one(
        "SELECT COUNT(*) as count FROM drafts WHERE status = 'rejected'"
    )

    total = total_row["count"] if total_row else 0
    published = published_row["count"] if published_row else 0
    rejected = rejected_row["count"] if rejected_row else 0

    # Get stats by version
    version_stats = await fetch_all(
        """
        SELECT
            prompt_version,
            COUNT(*) as total,
            SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published,
            SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected
        FROM drafts
        WHERE prompt_version IS NOT NULL
        GROUP BY prompt_version
        ORDER BY prompt_version DESC
        """
    )

    return templates.TemplateResponse(
        "pages/analytics.html",
        {
            "request": request,
            "total": total,
            "published": published,
            "rejected": rejected,
            "publish_rate": (published / total * 100) if total > 0 else 0,
            "version_stats": version_stats,
        },
    )


@app.get("/published", response_class=HTMLResponse)
async def published_page(request: Request):
    """Archive of published posts."""
    posts = await fetch_all(
        """
        SELECT * FROM published_posts
        ORDER BY published_at DESC
        LIMIT 100
        """
    )

    return templates.TemplateResponse(
        "pages/published.html",
        {"request": request, "posts": posts},
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
