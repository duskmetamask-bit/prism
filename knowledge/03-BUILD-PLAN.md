# PRISM — BUILD PLAN
**Status:** Foundation research COMPLETE | Build not started
**Date:** 2026-04-22
**Built by:** MEWY + Research

---

## WHERE WE ARE

### DONE — Knowledge Foundation (Phase 0)

```
✅ SOUL.md — Content philosophy + voice rules
✅ SPEC.md — What PRISM is, architecture, phases
✅ platform_algos.md — X, LinkedIn, YouTube, Newsletter mechanics
✅ content_principles.md — Hooks, structure, momentum, CTAs
✅ ELITE-RESEARCH.md — Competitive landscape, tools, market gap
✅ BUILD-EVOLUTION-GUIDE.md — How to build + iterate
✅ research-accounts-2026-04-22.md — 7 real growing accounts + WHY
✅ research-viral-posts-2026-04-22.md — 20 viral hook formulas + breakdowns
```

This is PRISM's knowledge brain. It knows the theory.

---

## WHAT WE NEED TO BUILD NEXT (Phase 1 — MVP)

### The MVP Goal
PRISM generates a week's worth of X content (draft), user reviews and approves, content gets pushed to Buffer queue manually (no API needed yet).

**Why this first:** No API costs, validates the content quality, tests the workflow, learns what sounds right before automating.

---

### FILES TO BUILD (Priority Order)

#### 1. Content Bank (Database)
```
database/
└── schema.sql          ← Creates tables in Supabase
```

**Tables:**
- `posts` — every content piece created
- `hooks` — hook type + performance score
- `topics` — topics + engagement rates
- `drafts` — content pending review
- `user_profile` — voice, goals, platforms, topics

**Why first:** Everything PRISM generates gets stored here. Without this, there's no memory.

---

#### 2. User Profile Config
```
config/
└── user-profile.yaml   ← Fill in once, PRISM reads forever
```

**What it contains:**
```yaml
name: Dusk
topics:
  - AI agents and automation
  - Building in public / "Shut Up and Build"
  - Crypto / Web3
  - Business growth for tradies and SMBs
voice:
  style: Direct, no fluff, actionable
  tone: Confident, sometimes contrarian
  avoids: Corporate speak, vague claims, engagement bait
goals:
  primary: Grow following, establish authority
  platforms: X (primary), LinkedIn (secondary), YouTube (future)
  frequency: 5-7 posts/week on X
  posting_window: "9am AWST, 12pm AWST, 6pm AWST"
```

**You fill this once. PRISM reads it for every piece.**

---

#### 3. Content Brain (Orchestrator)
```
engine/
└── content-brain.py
```

**What it does:**
- Takes: topic from user profile
- Takes: top-performing hook type from content bank (or default)
- Generates: content brief (hook type + premise + key insight)

**Input example:**
```python
generate_content_brief(topic="AI agents for tradies", user_profile=user_profile)
```

**Output example:**
```python
{
    "topic": "AI agents for tradies",
    "hook_type": "specificity",  # from 20-hook library
    "hook_variant": "I spent 6 months testing AI tools for tradies. One insight changed everything.",
    "premise": "Most tradies think AI is too complex/expensive. The reality is different.",
    "platform": "X",
    "format": "thread",
    "thread_length": "5 tweets",
    "cta": "Save this if you know a tradie who needs to hear this"
}
```

---

#### 4. X Writer (Platform Writer)
```
engine/
└── platform-writers/
    └── x-writer.py
```

**What it does:**
- Takes: content brief from content brain
- Takes: platform rules from knowledge (platform_algos.md)
- Takes: content principles from knowledge (content_principles.md)
- Takes: user voice from user-profile.yaml
- Outputs: X thread draft (5-7 tweets), saved to drafts/

**It should:**
- Write in user's voice (from user-profile.yaml)
- Enforce X rules (280 char limit, link in reply, no hashtag flooding)
- Use the hook type from the brief
- Include a CTA at the end
- Save each tweet separately for easy review

**Output:**
```
drafts/
└── 2026-04-27/
    ├── brief-001.md          ← The content brief PRISM used
    ├── tweet-01-hook.md      ← The hook tweet
    ├── tweet-02-point-1.md
    ├── tweet-03-point-2.md
    ├── tweet-04-point-3.md
    ├── tweet-05-cta.md
    └── meta.json             ← Hook type, topic, why this was chosen
```

---

#### 5. Visual Pipeline (Quote Cards)
```
engine/
└── visual-pipeline.py
```

**What it does:**
- Takes: key line from thread (e.g. "Most tradies think AI is too expensive. Here's the truth.")
- Generates: 2-3 quote card images using Ideogram API
- Saves: to drafts folder for review

**What we need first:** Ideogram API key (free tier available)

**If no API key yet:** PRISM generates a text description of what the quote card should look like, user creates manually.

---

#### 6. Weekly Generation Script
```
scripts/
└── generate-weekly.py
```

**What it does:**
```
1. Load user profile from config/
2. Check content bank for top-performing hooks/topics
3. Pick 3-5 topics for the week
4. For each topic → run content-brain → run x-writer
5. For each thread → run visual-pipeline (or generate text descriptions)
6. Save all drafts to drafts/YYYY-MM-DD/
7. DM user on Telegram: "Weekly content ready for review"
```

**Trigger:** On-demand via DM to Hermes, or cron job weekly

---

## WHAT WE DON'T BUILD YET (No API costs)

| What | Why Skip | When to Add |
|------|---------|-------------|
| Buffer API | Can paste content manually for now | When MVP validated |
| X API | No analytics needed yet | When we want auto-posting |
| LinkedIn writer | Start with X first | After X is validated |
| YouTube writer | Lower priority | After LinkedIn |
| Auto-publishing | Test quality first | After 10+ approved posts |
| Learning loop (analytics) | No data to learn from yet | After posts are live |

---

## THE WORKFLOW (How It Works Right Now)

```
YOU                         PRISM
 │                            │
 │  "generate this week's     │
 │   content"                 │
 │ ─────────────────────────► │
 │                            │ Load user profile
 │                            │ Check content bank
 │                            │ Pick 3 topics
 │                            │ Generate 3-5 content briefs
 │                            │ Write 3-5 X threads
 │                            │ Generate quote card ideas
 │                            │ Save to drafts/
 │                            │
 │  [Telegram DM]             │
 │  "Weekly content ready.    │
 │   3 threads in drafts."   │
 │ ◄───────────────────────── │
 │                            │
 │  Review each tweet         │
 │  Edit if needed            │
 │  Copy → Buffer manually    │
 │                            │
 │  [After posting]           │
 │  "Post 2 hit, Post 1 flopped"│
 │ ─────────────────────────► │
 │                            │ Record performance in content bank
 │                            │ Learn: specificity hook > contrarian for this audience
 │                            │
```

---

## WHAT PRISM KNOWS (The Knowledge Files)

When writing any content, PRISM reads:

```
~/.hermes/agents/prism/
├── knowledge/
│   ├── platform_algos.md      ← Platform rules (X char limits, algo signals)
│   ├── content_principles.md   ← Hooks, structure, what makes content hit
│   ├── research-accounts-2026-04-22.md  ← 7 real accounts + WHY they grow
│   └── research-viral-posts-2026-04-22.md ← 20 viral hook formulas
├── config/
│   └── user-profile.yaml      ← Your voice, topics, goals
└── database/
    └── content-bank.db        ← Posts + performance (grows over time)
```

---

## THE 20 HOOKS PRISM CAN USE (from research)

These are the proven hooks from real viral posts:

| # | Hook Formula |
|---|-------------|
| 1 | "[Specific thing] is dead. Here's why." |
| 2 | "You don't need [expensive thing]. You need [simple thing]." |
| 3 | "I spent $[specific] testing [category]. Here's what 90% taught me." |
| 4 | "Most people do [X] wrong. Do this instead." |
| 5 | "The #1 mistake [audience] makes is [specific]" |
| 6 | "After [N] of [activity], [specific finding]" |
| 7 | "[Audience]: stop doing [X]. Do [Y] instead." |
| 8 | "The only [topic] advice worth following in 2026" |
| 9 | "I asked [N] [professionals] what their [mistake] was. [Finding]." |
| 10 | "[Product/service] hit $[specific] MRR — [1 lesson]" |
| 11 | "Day [N] of [challenge]: [update]" |
| 12 | "I almost gave up at [moment]. [What changed]." |
| 13 | "I was wrong about [X] for [time]. Here's what I learned." |
| 14 | "Most people don't know [specific]. Here's the truth." |
| 15 | "[Bold prediction] about [your industry]." |
| 16 | "The [N] signs you're about to [mistake/miss]" |
| 17 | "Built [X] in [time]. [Outcome]." |
| 18 | "This week I tested [X]. [Surprising result]." |
| 19 | "If you've ever [painful situation], this is for you." |
| 20 | "The [N] things I wish I knew before [significant event]" |

---

## CONTENT TYPE MIX (Based on Real Account Data)

For every week of content:

| Content Type | % | Example |
|-------------|---|---------|
| Personal story / building in public | 30% | "I almost gave up on..." |
| Specific tips / lessons | 25% | "The [N] things I learned..." |
| Hot take / contrarian | 20% | "[X] is wrong because..." |
| Tool / resource | 15% | "I tested [tool] for 30 days..." |
| Engagement / question | 10% | "What would you do in my position?" |

---

## SUPABASE SCHEMA (Ready to Create)

```sql
-- USER PROFILE
CREATE TABLE user_profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT,
    topics TEXT[], -- array of topics
    voice_style TEXT,
    voice_tone TEXT,
    voice_avoids TEXT[],
    goals_primary TEXT,
    goals_platforms TEXT[],
    posting_windows TEXT[], -- ["9am AWST", "12pm AWST", "6pm AWST"]
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- CONTENT HOOKS LIBRARY
CREATE TABLE hooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hook_type TEXT, -- "counterintuitive", "specificity", "story", etc
    hook_formula TEXT, -- the actual template
    times_used INT DEFAULT 0,
    times_hit INT DEFAULT 0, -- "hit" = above average engagement
    avg_engagement JSONB, -- {"likes": 0, "saves": 0, "replies": 0}
    last_used TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- TOPICS
CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic TEXT UNIQUE,
    posts_created INT DEFAULT 0,
    avg_engagement JSONB,
    last_used TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- DRAFTS (pending review)
CREATE TABLE drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic TEXT,
    hook_type TEXT,
    platform TEXT, -- "X", "LinkedIn", "Newsletter"
    format TEXT, -- "thread", "single", "carousel"
    content JSONB, -- {"tweets": [...], "quote_cards": [...]}
    status TEXT DEFAULT 'pending', -- "pending", "approved", "rejected"
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- PUBLISHED POSTS
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID REFERENCES drafts(id),
    platform TEXT,
    content JSONB,
    hook_type TEXT,
    topic TEXT,
    posted_at TIMESTAMPTZ,
    -- Performance (filled in manually or via API later)
    impressions INT,
    likes INT,
    saves INT,
    replies INT,
    reposts INT,
    new_followers INT,
    engagement_rate FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## THE REALISTIC BUILD TIMELINE

| Week | What We Build | What's Working |
|------|--------------|---------------|
| 1 (THIS WEEK) | Supabase schema + User profile + Content brain + X writer | Can generate first draft manually |
| 2 | Hook up 3 example topics → generate 5 threads | Quality check: does it sound like you? |
| 3 | Visual pipeline (Ideogram) + Quote cards | Test visual workflow |
| 4 | User tests: review → edit → post manually | Does the workflow feel right? |
| 5-8 | Buffer API → Auto-schedule | Remove manual steps |
| 9-12 | Learning loop → Analytics | PRISM starts learning |

---

## WHAT I NEED FROM YOU TO START

**To build Week 1:**

1. **Supabase project** — do you have one running? (We have one for CALLIE, can use same project or new one)
2. **Your topics** — what 3-5 topics should PRISM generate content about?
3. **Your voice** — how would you describe your style in 3 sentences?
4. **Ideogram API** — do you want to set this up now or skip visuals for now?

Answer those and I'll build the content brain and X writer this week.
