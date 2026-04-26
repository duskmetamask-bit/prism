# PRISM — SPEC
**Status:** Phase 1 — CORE COMPLETE | scheduler + unified class added 2026-04-23
**Built by:** MEWY
**Date:** 2026-04-22

## What It Is
PRISM is Dusk's personal content intelligence agent. It generates platform-native content for X, LinkedIn, YouTube, and newsletters — and learns from every post's performance to get smarter over time.

**Core principle:** Platform mechanics + content principles = foundation. Personalisation layer = configured per user. Compound learning = the advantage.

## Architecture
```
prism (Hermes sub-agent)
├── engine/
│   ├── content-brain.py       ← decides WHAT to post
│   ├── calendar.py            ← decides WHEN to post
│   └── platform-writers/
│       ├── x-writer.py         ← X thread generator
│       └── linkedin-writer.py ← LinkedIn generator
├── database/                  ← SQLite (local MVP)
│   └── prism.db
├── config/
│   └── user-profile.yaml      ← voice, topics, goals
├── drafts/                   ← generated content for review
└── scripts/
    └── generate-weekly.py     ← cron/on-demand trigger
```

## Supabase Schema (rrjktvvnzjzlfquaghut.supabase.co)

```sql
-- USER PROFILE
CREATE TABLE IF NOT EXISTS prism_user_profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    topics TEXT[] NOT NULL,
    voice_style TEXT,
    voice_tone TEXT,
    voice_avoids TEXT[],
    goals_primary TEXT,
    goals_platforms TEXT[],
    posting_windows TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- CONTENT HOOKS LIBRARY (20 proven formulas)
CREATE TABLE IF NOT EXISTS prism_hooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hook_type TEXT NOT NULL,
    hook_formula TEXT NOT NULL,
    times_used INT DEFAULT 0,
    times_hit INT DEFAULT 0,
    avg_likes INT DEFAULT 0,
    avg_saves INT DEFAULT 0,
    avg_replies INT DEFAULT 0,
    last_used TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- TOPICS
CREATE TABLE IF NOT EXISTS prism_topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic TEXT UNIQUE NOT NULL,
    posts_created INT DEFAULT 0,
    avg_likes INT DEFAULT 0,
    avg_saves INT DEFAULT 0,
    last_used TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- DRAFTS (pending review)
CREATE TABLE IF NOT EXISTS prism_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic TEXT NOT NULL,
    hook_type TEXT NOT NULL,
    hook_formula TEXT,
    platform TEXT NOT NULL DEFAULT 'X',
    format TEXT NOT NULL DEFAULT 'thread',
    content JSONB NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- PUBLISHED POSTS
CREATE TABLE IF NOT EXISTS prism_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID REFERENCES prism_drafts(id),
    platform TEXT NOT NULL,
    content JSONB NOT NULL,
    hook_type TEXT,
    topic TEXT,
    posted_at TIMESTAMPTZ,
    impressions INT DEFAULT 0,
    likes INT DEFAULT 0,
    saves INT DEFAULT 0,
    replies INT DEFAULT 0,
    reposts INT DEFAULT 0,
    new_followers INT DEFAULT 0,
    engagement_rate FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## The 20 Proven Hooks

| # | Hook Formula | Type |
|---|-------------|------|
| 1 | "[Specific thing] is dead. Here's why." | Counterintuitive |
| 2 | "You don't need [expensive thing]. You need [simple thing]." | Contrarian |
| 3 | "I spent $[specific] testing [category]. Here's what 90% taught me." | Specificity |
| 4 | "Most people do [X] wrong. Do this instead." | Contrarian |
| 5 | "The #1 mistake [audience] makes is [specific]" | Authority |
| 6 | "After [N] of [activity], [specific finding]" | Authority |
| 7 | "[Audience]: stop doing [X]. Do [Y] instead." | Direct |
| 8 | "The only [topic] advice worth following in 2026" | Authority |
| 9 | "I asked [N] [professionals] what their [mistake] was. [Finding]." | Social Proof |
| 10 | "[Product/service] hit $[specific] MRR — [1 lesson]" | Milestone |
| 11 | "Day [N] of [challenge]: [update]" | Diary |
| 12 | "I almost gave up at [moment]. [What changed]." | Story |
| 13 | "I was wrong about [X] for [time]. Here's what I learned." | Confession |
| 14 | "Most people don't know [specific]. Here's the truth." | Hidden Info |
| 15 | "[Bold prediction] about [your industry]." | Prediction |
| 16 | "The [N] signs you're about to [mistake/miss]" | Warning |
| 17 | "Built [X] in [time]. [Outcome]." | Ship Story |
| 18 | "This week I tested [X]. [Surprising result]." | Experiment |
| 19 | "If you've ever [painful situation], this is for you." | Recognition |
| 20 | "The [N] things I wish I knew before [significant event]" | Lessons |

## Phase Status
- ✅ Phase 0: Knowledge foundation (platform_algos, content_principles, research)
- ✅ Phase 1: Core engine (content-brain, x-writer, database, config, scheduler, unified class)
- ⬜ Phase 2: Visual pipeline (Ideogram integration)
- ⬜ Phase 3: Buffer API (auto-scheduling)
- ⬜ Phase 4: Multi-platform (LinkedIn, YouTube writers)
- ⬜ Phase 5: Learning loop (analytics → content bank updates)

**Note (2026-04-25): CLARKE is ARCHIVED. PRISM is the sole content intelligence agent. No separate research layer. Dusk picks topics → PRISM generates → Dusk approves → post.**

## Content Scheduling Engine — Algorithm Windows
Platform-specific posting windows (AWST):

| Platform | Best Days | Windows | Posts/Week | Why |
|----------|-----------|---------|------------|-----|
| X | Mon–Fri | 9am, 12pm, 6pm | 5–7 | Engagement peaks mid-morning, lunch, evening |
| LinkedIn | Tue, Wed, Thu | 8am | 2–3 | Algorithm rewards early-week professional content |
| YouTube | Thu–Sun | 3pm, 5pm, 6pm | 1–2 | Viewership peaks Thu–Sun evenings |

Content type mix target:
- 30% personal story
- 25% tips/lessons
- 20% hot take
- 15% tool/resource
- 10% engagement (questions, callouts)
