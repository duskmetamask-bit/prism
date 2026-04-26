# PRISM — BUILD & EVOLUTION GUIDE
**Purpose:** How to build PRISM correctly and evolve it over time
**Based on:** Elite research + AI agent playbook best practices + multi-agent architecture patterns
**Last updated:** 2026-04-22

---

## PART 1: HOW TO BUILD PRISM CORRECTLY

### The Right Build Order

**Phase 0 — Foundation (DONE)**
```
✅ platform_algos.md — platform mechanics (never changes)
✅ content_principles.md — content laws (never changes)
✅ ELITE-RESEARCH.md — competitive intelligence
✅ SOUL.md — content philosophy + voice rules
```

These files are the expert system. They never change per user. They are PRISM's knowledge base.

**Phase 1 — The Brain**
```
NEXT: content-brain (orchestrator)
- Topic selection engine
- Premise generation
- Content repurposing logic (1 → many)
- Content type rotation logic
```

**Phase 2 — The Calendar**
```
THEN: calendar (scheduler)
- Posting schedule manager
- Platform-specific optimal windows
- Content type cadence
- Flood penalty prevention
```

**Phase 3 — Platform Writers (in order)**
```
1. X writer (highest volume, fastest feedback loop)
2. LinkedIn writer
3. Newsletter writer
4. YouTube agent
5. Visual pipeline
```

**Phase 4 — The Loop**
```
FINALLY: learning system
- Analytics ingestion
- Performance → content bank
- Hook/format/topic scoring
```

---

## PART 2: THE AGENT ARCHITECTURE PATTERN

### The Orchestrator Pattern (How PRISM Thinks)

```
User: "I want to post more"
         │
         ▼
┌─────────────────────────────────┐
│     PRISM ORCHESTRATOR          │
│                                 │
│  1. What should we post?         │ ← content-brain
│     (topic + premise)           │
│                                 │
│  2. How should it sound?         │ ← SOUL (voice)
│     (hook type + tone)          │
│                                 │
│  3. Where should it go?          │ ← calendar
│     (platform + timing)          │
│                                 │
│  4. How do we format it?         │ ← platform writer
│     (native format)              │
│                                 │
│  5. Does it need visuals?        │ ← visual pipeline
│     (thumbnail + cards)          │
│                                 │
│  6. When do we post?             │ ← calendar
│     (optimal window)             │
│                                 │
│  7. Did it work?                 │ ← learning loop
│     (track → update bank)       │
└─────────────────────────────────┘
```

### The Handoff Protocol

Each component passes data in a defined format:

```python
# content-brain → platform writer
{
    "topic": "AI delegation",
    "premise": "Most founders do too much themselves. Here's what to delegate first.",
    "hook_type": "counterintuitive",
    "hook_variants": ["Most founders are doing it backwards", "Stop doing X until you've done Y"],
    "target_platform": "X",
    "content_type": "thread",
    "key_insight": "The first thing to delegate is the thing you're best at"
}

# platform writer → visual pipeline
{
    "content_piece": "The full X thread text",
    "key_line": "Most founders are doing it backwards — here's what to delegate first",
    "format": "quote_card",
    "platform": "X",
    "style_hint": "Bold, high contrast, text-forward"
}

# post published → learning loop
{
    "post_id": "x_123456",
    "platform": "X",
    "hook_type": "counterintuitive",
    "topic": "AI delegation",
    "posted_at": "2026-04-22 09:00 AWST",
    "impressions": 4200,
    "engagements": 312,
    "saves": 47,
    "new_followers_from_post": 23
}
```

---

## PART 3: HOW PRISM LEARNS (THE COMPOUND EFFECT)

### The Feedback Loop

```
EVERY POST gets tracked:
┌──────────────────────────────────────────────────────┐
│  Hook type?     →  saves rate                        │
│  Topic?         →  new followers                     │
│  Format?        →  engagement rate                   │
│  Posted at?     →  impression reach                  │
│  Content type?   →  all of the above                  │
└──────────────────────────────────────────────────────┘
         │
         ▼
PRISM CONTENT BANK gets updated with real performance data
         │
         ▼
NEXT content decision is SMARTER
```

### What PRISM Tracks Per Post

| Signal | What It Tells PRISM |
|--------|---------------------|
| Saves rate | Content depth/resonance |
| New followers from post | Topic authority |
| Engagement velocity | Hook strength |
| Reply depth | Conversation generation |
| CTR (YouTube) | Thumbnail + title strength |
| Watch time (YouTube) | Content hold |
| Open rate (newsletter) | Subject line + preview text |
| Click rate (newsletter) | CTA placement |

### The Content Bank Structure

```
PRISM CONTENT BANK
│
├── hooks/
│   ├── counterintuitive/     (hook type + performance score)
│   ├── specificity/          (hook type + performance score)
│   ├── recognition/          (hook type + performance score)
│   ├── authority/            (hook type + performance score)
│   └── story/                (hook type + performance score)
│
├── topics/
│   ├── [topic_name]/         (engagement rate, save rate, new follower rate)
│   └── evergreen_pillars/     (topics that always perform)
│
├── formats/
│   ├── thread/              (avg engagement by thread length)
│   ├── single_post/         (avg engagement)
│   ├── carousel/            (avg engagement)
│   └── video/               (avg watch time, CTR)
│
└── timing/
    └── [platform]/          (best windows for THIS user's audience)
```

---

## PART 4: EVOLUTION ROADMAP

### Version 1 (Now) — The Core
```
✅ Platform algorithms knowledge base
✅ Content principles knowledge base
✅ Elite research
⬜ Content brain (orchestrator logic)
⬜ Calendar system
⬜ X writer
⬜ Learning loop (basic)
```
**What it does:** PRISM can generate and schedule X posts with a basic learning loop.

### Version 2 (Next) — Multi-Platform
```
✅ Everything in v1
⬜ LinkedIn writer
⬜ Newsletter writer
⬜ YouTube agent
⬜ Visual pipeline (Ideogram/FLUX integration)
⬜ Content repurposing (1 piece → all platforms)
```
**What it does:** True cross-platform content machine. One YouTube video → all formats.

### Version 3 (Later) — Intelligent
```
✅ Everything in v2
⬜ Trend detection (real-time topic intelligence)
⬜ Competitor monitoring (what's working in your space)
⬜ A/B headline testing
⬜ Audience growth prediction
⬜ Content gap analysis (what topics you're missing)
```
**What it does:** PRISM stops reacting and starts predicting.

### Version 4 (Future) — Autonomous
```
✅ Everything in v3
⬜ Fully autonomous posting (no human in loop for posting)
⬜ PRISM proposes → user approves → PRISM posts
⬜ Cross-platform content calendar built automatically
⬜ Voice fine-tuning (learns from every correction)
⬜ White-label client portal (productised)
```
**What it does:** Fully autonomous content machine. User becomes editor, not creator.

---

## PART 5: BUILD BEST PRACTICES

### How to Build Each Platform Writer

Following the Agent Design 4 pattern from the AI Agent Playbook:

**STAGE 1 — SOURCE & RESEARCH**
```
What triggers a new content piece?
- Content brief from orchestrator (topic + premise + hook type)
- Past performance data (what has worked in this category)
- Platform-specific optimal timing

What does the agent capture?
- Topic + premise + hook
- Target word count
- Target format
```

**STAGE 2 — DRAFT**
```
What does the first draft look like?
- Follows content principles (hook first, substance second)
- Platform-native format (character limits, paragraph rules)
- Voice matches user's trained voice profile

What is the length and format?
- X: 1-280 chars (single), 5-10 tweets (thread)
- LinkedIn: 150-300 words (post), 5-10 slides (carousel)
- Newsletter: 400-600 words (body)
- YouTube: Hook (30 sec) + body (8-15 min)
```

**STAGE 3 — EDIT & OPTIMIZE**
```
What does human editing add?
- Voice authenticity check
- Specific anecdotes to incorporate
- Corrections to any factual errors

What can the agent already handle?
- Platform-specific optimization
- Hashtag ceiling enforcement
- CTA placement
- Format compliance
```

**STAGE 4 — SCHEDULE & POST**
```
How does content get scheduled?
- API → Buffer/SocialBee queue
- Platform-specific optimal windows
- Content type rotation (no two educational in a row)

Is there an approval step?
- YES for us (at least v1-v2)
- NO for productised version (fully autonomous)
```

### Content Variations Per Piece

For each content piece, PRISM generates:

```
PRIMARY: [Platform-native post]
REPLY VARIANTS: [2-3 engagement reply options]
THREAD VERSION: [If primary is single post, also thread version]
LINKEDIN ADAPTATION: [If different platform]
QUOTE CARDS: [3 key lines → 3 images]
YOUTUBE SHORT: [Hook + 1 key insight script]
```

### Voice Training System

**Step 1 — Initial Setup:**
User completes questionnaire:
- "What topics do you post about?"
- "What would you NEVER say in a post?"
- "Give 3 example posts you've written that you loved"
- "What's your posting goal? (grow followers / build authority / sell)"

**Step 2 — Feedback Loop:**
After each post:
- User approves / rejects
- If rejected: why? (too corporate / too casual / wrong angle / factually wrong)
- PRISM updates voice profile

**Step 3 — Pattern Recognition:**
After 20 posts, PRISM can identify:
- Your typical hook style
- Your sentence length tendencies
- Words you use vs don't use
- Your perspective (teacher vs storyteller vs challenger)

---

## PART 6: WHAT PRISM NEVER DOES (NON-NEGOTIABLE)

These are the anti-patterns that separate elite from average:

```
1. NEVER post identical content to multiple platforms
   → Must be rewritten for each platform's grammar

2. NEVER use engagement bait
   → "Like if you agree" = algo penalty + robotic

3. NEVER post more than optimal frequency
   → Flood penalty is real on X, low-value signal on LinkedIn

4. NEVER use more hashtags than platform ceiling
   → LinkedIn: 3-5 max, X: 1-3 max

5. NEVER sacrifice authenticity for volume
   → Better 3 real posts than 10 generic ones

6. NEVER claim results without context
   → "I made $1M" without how = trust erodes

7. NEVER sound corporate
   → "We're excited to announce" = death

8. NEVER recommend fake engagement
   → Follower buying / engagement pods = algorithmic poison

9. NEVER post purely for algo benefit
   → If it doesn't serve the audience, it won't serve the algo

10. NEVER guess at platform rules
    → If PRISM doesn't know, it asks before posting
```

---

## PART 7: MEASURING SUCCESS

### PRISM's North Star Metrics

| Metric | What It Measures |
|--------|-----------------|
| Saves rate | Content depth (people bookmark = valuable) |
| New followers from post | Topic authority |
| Engagement velocity (first 2 hours) | Hook strength |
| Content bank hit rate | What % of content uses proven hooks |

### Milestone Markers

- **Post 10:** PRISM has basic performance data, can identify first patterns
- **Post 50:** Content bank is statistically significant, clear hook type winner
- **Post 100:** PRISM knows optimal posting window for YOUR audience
- **Post 200:** PRISM can predict with reasonable accuracy what will hit BEFORE posting
- **Post 500:** PRISM is genuinely smarter than most human social media managers

---

## PART 8: HOW TO ITERATE PRISM

### The Iteration Cycle

```
Week 1-2: Build core components
↓ Test on real posts (even if just draft, not publish)
↓ User reviews, flags issues
↓ PRISM updates based on feedback

Week 3-4: Hook up scheduling
↓ Publish real posts
↓ Start tracking performance
↓ Learning loop activates

Month 2: Multi-platform
↓ Add LinkedIn
↓ Add newsletter
↓ Content repurposing active

Month 3+: Autonomous operation
↓ PRISM proposes
↓ User approves
↓ PRISM publishes
↓
↓ User corrects
↓ PRISM learns
↓
↓ Corrections decrease
↓
↓ Fully autonomous
```

### What to Build vs Buy

| Component | Build | Buy |
|-----------|-------|-----|
| Content brain | BUILD (our IP) | — |
| Platform writers | BUILD (our IP) | — |
| Visual generation | — | Ideogram/FLUX API |
| Scheduling | — | Buffer/SocialBee API |
| Analytics | Native + API | — |
| Learning loop | BUILD | — |
| Voice training | BUILD | — |

### The Key Constraint

**PRISM must always be able to explain WHY it made a content decision.**

Not just "generated a post about AI" — but:
- "This hook type had a 23% save rate in your content bank vs 8% average"
- "This topic drove your highest new-follower-per-post in the last 30 days"
- "Posted at this time because your audience is most active at 8am AWST on Wednesdays"

If PRISM can't explain it, it doesn't post it.

---

## SUMMARY: THE ELITE PRINCIPLE

**Build it like a human would learn.**

A human social media manager:
1. Posts something
2. Watches what hits
3. Does more of what worked
4. Avoids what didn't
5. Gets better over time

PRISM does all of this — but at scale, without fatigue, and with perfect memory.

That's the compound effect. That's what makes it elite.

**The content bank is the asset. The learning loop is the engine. The platform intelligence is the advantage.**

Everything else is just automation.
