-- Add feedback tracking fields for learning

-- Rejection reason: captures why a draft was rejected
ALTER TABLE drafts ADD COLUMN rejection_reason TEXT;

-- Edit notes: captures what was changed and why during editing
ALTER TABLE drafts ADD COLUMN edit_notes TEXT;

-- Published without edits: flag for exemplar posts (true = no edits needed)
ALTER TABLE drafts ADD COLUMN published_without_edits INTEGER DEFAULT 0;

-- Status now includes 'banked' for save-for-later
-- Existing values: pending/edited/published/rejected
-- New value: banked (saved for later refinement)

-- Voice score: track how well the draft used personal voice (1-5)
ALTER TABLE drafts ADD COLUMN voice_score INTEGER;

-- Feedback table for structured learning
CREATE TABLE IF NOT EXISTS draft_feedback (
    id TEXT PRIMARY KEY,
    draft_id TEXT NOT NULL,
    feedback_type TEXT NOT NULL,  -- 'rejection', 'edit', 'exemplar', 'banked'
    reason TEXT,                   -- Why this action was taken
    original_snippet TEXT,         -- What was changed (for edits)
    revised_snippet TEXT,          -- What it became (for edits)
    created_at INTEGER NOT NULL,
    FOREIGN KEY (draft_id) REFERENCES drafts(id)
);

CREATE INDEX IF NOT EXISTS idx_draft_feedback_type ON draft_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_draft_feedback_draft_id ON draft_feedback(draft_id);
