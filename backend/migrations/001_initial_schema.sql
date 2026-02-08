-- drafts
CREATE TABLE IF NOT EXISTS drafts (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    title TEXT,
    summary TEXT,
    tags TEXT,                  -- JSON array
    style_type TEXT,
    prompt_version TEXT,
    batch_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending/edited/published/rejected
    edited_content TEXT,
    generated_at INTEGER NOT NULL,
    published_at INTEGER,
    github_commit_sha TEXT
);

-- prompt_versions
CREATE TABLE IF NOT EXISTS prompt_versions (
    version TEXT PRIMARY KEY,
    instructions TEXT NOT NULL,
    context TEXT,
    notes TEXT,
    is_active INTEGER DEFAULT 0,
    created_at INTEGER NOT NULL
);

-- published_posts
CREATE TABLE IF NOT EXISTS published_posts (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    slug TEXT NOT NULL,
    content TEXT NOT NULL,
    published_at INTEGER NOT NULL,
    prompt_version TEXT,
    edit_time_seconds INTEGER,
    github_url TEXT
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_drafts_status ON drafts(status);
CREATE INDEX IF NOT EXISTS idx_drafts_batch_id ON drafts(batch_id);
CREATE INDEX IF NOT EXISTS idx_drafts_generated_at ON drafts(generated_at);
CREATE INDEX IF NOT EXISTS idx_prompt_versions_is_active ON prompt_versions(is_active);
CREATE INDEX IF NOT EXISTS idx_published_posts_published_at ON published_posts(published_at);
