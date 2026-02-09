from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Draft models
class DraftBase(BaseModel):
    content: str
    title: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    style_type: Optional[str] = None
    prompt_version: Optional[str] = None


class DraftCreate(DraftBase):
    pass


class DraftUpdate(BaseModel):
    content: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    edited_content: Optional[str] = None
    edit_notes: Optional[str] = None
    voice_score: Optional[int] = None  # 1-5 rating


class Draft(DraftBase):
    id: str
    batch_id: str
    status: str  # pending, edited, published, rejected, banked
    edited_content: Optional[str] = None
    generated_at: int
    published_at: Optional[int] = None
    github_commit_sha: Optional[str] = None
    # Feedback tracking
    rejection_reason: Optional[str] = None
    edit_notes: Optional[str] = None
    published_without_edits: bool = False
    voice_score: Optional[int] = None

    class Config:
        from_attributes = True


class DraftBatch(BaseModel):
    batch_id: str
    generated_at: int
    drafts: List[Draft]


# Batch submission from GitHub Actions
class BatchSubmission(BaseModel):
    drafts: List[DraftCreate]
    prompt_version: Optional[str] = None


# Prompt version models
class PromptVersionBase(BaseModel):
    instructions: str
    context: Optional[str] = None
    notes: Optional[str] = None


class PromptVersionCreate(PromptVersionBase):
    version: str


class PromptVersion(PromptVersionBase):
    version: str
    is_active: bool
    created_at: int

    class Config:
        from_attributes = True


# Published post models
class PublishedPost(BaseModel):
    id: str
    title: str
    slug: str
    content: str
    published_at: int
    prompt_version: Optional[str] = None
    edit_time_seconds: Optional[int] = None
    github_url: Optional[str] = None

    class Config:
        from_attributes = True


# Analytics models
class PromptVersionStats(BaseModel):
    version: str
    total_drafts: int
    published_count: int
    rejected_count: int
    pending_count: int
    publish_rate: float
    avg_edit_time_seconds: Optional[float] = None


class AnalyticsSummary(BaseModel):
    total_drafts: int
    total_published: int
    total_rejected: int
    overall_publish_rate: float
    by_version: List[PromptVersionStats]


# Feedback models
class RejectRequest(BaseModel):
    reason: Optional[str] = None  # Why was this draft rejected?


class BankRequest(BaseModel):
    notes: Optional[str] = None  # Notes for saving for later


# API response models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class PublishResult(BaseModel):
    success: bool
    github_url: Optional[str] = None
    commit_sha: Optional[str] = None
    error: Optional[str] = None
