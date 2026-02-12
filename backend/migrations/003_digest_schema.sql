-- Daily digest tables for Market Watch newsletter

-- Main digest storage
CREATE TABLE IF NOT EXISTS daily_digests (
    id TEXT PRIMARY KEY,
    date_iso TEXT NOT NULL UNIQUE,      -- YYYY-MM-DD
    status TEXT NOT NULL DEFAULT 'generating',  -- generating | draft | published | failed
    content TEXT,                        -- generated markdown
    sources_json TEXT DEFAULT '[]',      -- JSON array of {name, url, category}
    categories TEXT DEFAULT '[]',        -- JSON array of detected category slugs
    error_message TEXT,                  -- error details if failed
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

-- Single-row mutex table to prevent concurrent job runs
CREATE TABLE IF NOT EXISTS digest_job_state (
    id TEXT PRIMARY KEY,                 -- hardcoded: 00000000-0000-0000-0000-000000000001
    is_locked INTEGER DEFAULT 0,
    locked_at INTEGER,
    locked_by TEXT,
    last_run_at INTEGER,
    last_run_status TEXT
);

-- Seed with single row if not exists
INSERT OR IGNORE INTO digest_job_state (id, is_locked)
VALUES ('00000000-0000-0000-0000-000000000001', 0);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_daily_digests_date ON daily_digests(date_iso);
CREATE INDEX IF NOT EXISTS idx_daily_digests_status ON daily_digests(status);
