-- PRISM SQLite Schema (local MVP)
-- File: database/prism.db

-- USER PROFILE
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    topics TEXT NOT NULL,
    voice_style TEXT,
    voice_tone TEXT,
    voice_avoids TEXT,
    goals_primary TEXT,
    goals_platforms TEXT,
    posting_windows TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- CONTENT HOOKS LIBRARY (20 proven formulas)
CREATE TABLE IF NOT EXISTS hooks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hook_type TEXT NOT NULL,
    hook_formula TEXT NOT NULL,
    times_used INTEGER DEFAULT 0,
    times_hit INTEGER DEFAULT 0,
    avg_likes INTEGER DEFAULT 0,
    avg_saves INTEGER DEFAULT 0,
    avg_replies INTEGER DEFAULT 0,
    last_used TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- TOPICS
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT UNIQUE NOT NULL,
    posts_created INTEGER DEFAULT 0,
    avg_likes INTEGER DEFAULT 0,
    avg_saves INTEGER DEFAULT 0,
    last_used TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- DRAFTS (pending review)
CREATE TABLE IF NOT EXISTS drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    hook_type TEXT NOT NULL,
    hook_formula TEXT,
    platform TEXT NOT NULL DEFAULT 'X',
    format TEXT NOT NULL DEFAULT 'thread',
    content TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- PUBLISHED POSTS
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draft_id INTEGER REFERENCES drafts(id),
    platform TEXT NOT NULL,
    content TEXT NOT NULL,
    hook_type TEXT,
    topic TEXT,
    posted_at TEXT,
    impressions INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    reposts INTEGER DEFAULT 0,
    new_followers INTEGER DEFAULT 0,
    engagement_rate REAL,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Insert the 20 proven hooks
INSERT INTO hooks (hook_type, hook_formula) VALUES
('counterintuitive', '[Specific thing] is dead. Here''s why.'),
('contrarian', 'You don''t need [expensive thing]. You need [simple thing].'),
('specificity', 'I spent $[specific] testing [category]. Here''s what 90% taught me.'),
('contrarian', 'Most people do [X] wrong. Do this instead.'),
('authority', 'The #1 mistake [audience] makes is [specific]'),
('authority', 'After [N] of [activity], [specific finding]'),
('direct', '[Audience]: stop doing [X]. Do [Y] instead.'),
('authority', 'The only [topic] advice worth following in 2026'),
('social_proof', 'I asked [N] [professionals] what their [mistake] was. [Finding].'),
('milestone', '[Product/service] hit $[specific] MRR — [1 lesson]'),
('diary', 'Day [N] of [challenge]: [update]'),
('story', 'I almost gave up at [moment]. [What changed].'),
('confession', 'I was wrong about [X] for [time]. Here''s what I learned.'),
('hidden_info', 'Most people don''t know [specific]. Here''s the truth.'),
('prediction', '[Bold prediction] about [your industry].'),
('warning', 'The [N] signs you''re about to [mistake/miss]'),
('ship_story', 'Built [X] in [time]. [Outcome].'),
('experiment', 'This week I tested [X]. [Surprising result].'),
('recognition', 'If you''ve ever [painful situation], this is for you.'),
('lessons', 'The [N] things I wish I knew before [significant event]');
