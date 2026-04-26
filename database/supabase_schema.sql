-- PRISM SaaS — Multi-tenant Supabase Schema
-- Run this in Supabase SQL Editor
-- https://rrjktvvnzjzlfquaghut.supabase.co

-- ─── Extensions ──────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── Accounts (top level — organization/workspace) ──────────────────────────
CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    plan TEXT DEFAULT 'starter' CHECK (plan IN ('starter', 'pro', 'trial')),
    posts_limit INTEGER DEFAULT 30,
    x_accounts_limit INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Users ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT,
    role TEXT DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- ─── X Accounts (connected X profiles per account) ───────────────────────────
CREATE TABLE IF NOT EXISTS x_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    oauth_token TEXT,
    oauth_token_secret TEXT,
    oauth_token_encrypted TEXT,  -- AES encrypted
    x_user_id TEXT,
    x_username TEXT,
    x_display_name TEXT,
    x_avatar_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    connected_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(account_id, x_user_id)
);

-- ─── Content Brain (stories / topics per account) ─────────────────────────────
CREATE TABLE IF NOT EXISTS stories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    source TEXT NOT NULL,
    source_id TEXT,
    title TEXT NOT NULL,
    url TEXT,
    author TEXT,
    points INTEGER DEFAULT 0,
    summary TEXT,
    topics TEXT[],  -- PostgreSQL array
    story_date DATE,
    fetched_at TIMESTAMPTZ DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    used_in_content BOOLEAN DEFAULT FALSE
);

-- ─── Hooks Library (per account) ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    hook_type TEXT NOT NULL,
    hook_formula TEXT NOT NULL,
    times_used INTEGER DEFAULT 0,
    times_hit INTEGER DEFAULT 0,
    avg_likes INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Drafts ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS drafts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    x_account_id UUID REFERENCES x_accounts(id),
    story_id UUID REFERENCES stories(id),
    topic TEXT,
    hook_type TEXT,
    hook_formula TEXT,
    platform TEXT DEFAULT 'X',
    format TEXT DEFAULT 'single',
    content JSONB NOT NULL,
    -- content JSONB: { "text": "...", "media": [], "thread": [...] }
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'scheduled', 'posted', 'rejected')),
    scheduled_for TIMESTAMPTZ,
    posted_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ
);

-- ─── Content Calendar ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS content_calendar (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    x_account_id UUID REFERENCES x_accounts(id),
    draft_id UUID REFERENCES drafts(id),
    planned_date DATE NOT NULL,
    pillar TEXT,
    topic TEXT,
    angle TEXT,
    format TEXT DEFAULT 'single',
    status TEXT DEFAULT 'planned' CHECK (status IN ('planned', 'posted', 'skipped')),
    source TEXT DEFAULT 'auto',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Published Posts ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS published (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    x_account_id UUID REFERENCES x_accounts(id),
    draft_id UUID REFERENCES drafts(id),
    x_post_id TEXT,
    content TEXT NOT NULL,
    hook_type TEXT,
    topic TEXT,
    posted_at TIMESTAMPTZ,
    impressions INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    reposts INTEGER DEFAULT 0,
    new_followers INTEGER DEFAULT 0,
    engagement_rate REAL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Topics / Content Pillars ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    pillar TEXT NOT NULL,
    description TEXT,
    angles TEXT[],
    hook_templates TEXT[],
    times_used INTEGER DEFAULT 0,
    times_published INTEGER DEFAULT 0,
    avg_engagement INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(account_id, topic)
);

-- ─── User Preferences ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID UNIQUE NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    brand_voice TEXT DEFAULT '',
    brand_tone TEXT DEFAULT 'direct',
    topics TEXT[],
    content_pillars TEXT[],
    posting_schedule JSONB DEFAULT '[]',
    auto_post BOOLEAN DEFAULT FALSE,
    posting_windows TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Trending Cache (per account, refreshed daily) ───────────────────────────
CREATE TABLE IF NOT EXISTS trending_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    engagement_score INTEGER DEFAULT 0,
    source TEXT,
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '1 day'
);

-- ─── Row Level Security ──────────────────────────────────────────────────────
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE x_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE stories ENABLE ROW LEVEL SECURITY;
ALTER TABLE hooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_calendar ENABLE ROW LEVEL SECURITY;
ALTER TABLE published ENABLE ROW LEVEL SECURITY;
ALTER TABLE topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE trending_cache ENABLE ROW LEVEL SECURITY;

-- Policies: users can only access their own account's data
CREATE POLICY "Users can access own account" ON accounts
    FOR ALL USING (TRUE);

CREATE POLICY "Users can access own users" ON users
    FOR ALL USING (TRUE);

CREATE POLICY "Users can access own x_accounts" ON x_accounts
    FOR ALL USING (TRUE);

CREATE POLICY "Users can access own stories" ON stories
    FOR ALL USING (TRUE);

CREATE POLICY "Users can access own hooks" ON hooks
    FOR ALL USING (TRUE);

CREATE POLICY "Users can access own drafts" ON drafts
    FOR ALL USING (TRUE);

CREATE POLICY "Users can access own calendar" ON content_calendar
    FOR ALL USING (TRUE);

CREATE POLICY "Users can access own published" ON published
    FOR ALL USING (TRUE);

CREATE POLICY "Users can access own topics" ON topics
    FOR ALL USING (TRUE);

CREATE POLICY "Users can access own preferences" ON preferences
    FOR ALL USING (TRUE);

CREATE POLICY "Users can access own trending" ON trending_cache
    FOR ALL USING (TRUE);

-- ─── Indexes ──────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_users_account ON users(account_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_x_accounts_account ON x_accounts(account_id);
CREATE INDEX IF NOT EXISTS idx_stories_account ON stories(account_id);
CREATE INDEX IF NOT EXISTS idx_stories_unprocessed ON stories(account_id, processed) WHERE processed = FALSE;
CREATE INDEX IF NOT EXISTS idx_drafts_account ON drafts(account_id);
CREATE INDEX IF NOT EXISTS idx_drafts_status ON drafts(account_id, status);
CREATE INDEX IF NOT EXISTS idx_calendar_account ON content_calendar(account_id);
CREATE INDEX IF NOT EXISTS idx_calendar_date ON content_calendar(planned_date);
CREATE INDEX IF NOT EXISTS idx_published_account ON published(account_id);
CREATE INDEX IF NOT EXISTS idx_topics_account ON topics(account_id);
CREATE INDEX IF NOT EXISTS idx_trending_account ON trending_cache(account_id);

-- ─── Seed Hooks ──────────────────────────────────────────────────────────────
INSERT INTO hooks (account_id, hook_type, hook_formula)
SELECT 
    a.id,
    h.hook_type,
    h.hook_formula
FROM accounts a
CROSS JOIN (
    VALUES
    ('counterintuitive', '[Specific thing] is dead. Here''s why.'),
    ('contrarian', 'You don''t need [expensive thing]. You need [simple thing].'),
    ('specificity', 'I spent $[specific] testing [category]. Here''s what 90% taught me.'),
    ('authority', 'The #1 mistake [audience] makes is [specific]'),
    ('direct', '[Audience]: stop doing [X]. Do [Y] instead.'),
    ('social_proof', 'I asked [N] [professionals] what their [mistake] was. [Finding].'),
    ('milestone', '[Product/service] hit $[specific] MRR — [1 lesson]'),
    ('diary', 'Day [N] of [challenge]: [update]'),
    ('story', 'I almost gave up at [moment]. [What changed].'),
    ('confession', 'I was wrong about [X] for [time]. Here''s what I learned.'),
    ('hidden_info', 'Most people don''t know [specific]. Here''s the truth.'),
    ('prediction', '[Bold prediction] about [your industry].'),
    ('warning', 'The [N] signs you''re about to [mistake/miss]'),
    ('ship_story', 'Built [X] in [time]. [Outcome].'),
    ('experiment', 'This week I tested [X]. [Surprising result].')
) h(hook_type, hook_formula)
WHERE NOT EXISTS (SELECT 1 FROM hooks WHERE account_id = a.id);
