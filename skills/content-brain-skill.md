# Content Brain Skill
**For:** PRISM content agent
**Purpose:** How to manage the story brain — selecting, quality-filtering, and refreshing stories
**Last updated:** 2026-04-25

---

## What Is the Content Brain

The content brain is `prism.db` — a SQLite database of stories, trends, and insights PRISM draws from to generate content.

**Tables:**
- `stories` — raw stories fetched from sources (HN, X, Reddit, YouTube)
- `drafts` — generated posts awaiting human review
- `published` — posts that have gone live with engagement data
- `hooks` — hook library with performance tracking

---

## Story Selection Criteria

A story is worth using if it meets ALL 3:

1. **Specificity** — has real numbers, named tools, specific outcomes. Not vague trends.
2. **Relevance** — connects to Dusk's focus areas (AI agents, voice AI, infrastructure, building AI businesses)
3. **Angle potential** — can be twisted into a contrarian take, a "I built this", a "the pattern is", or a "here's what nobody talks about"

### Strong Story Indicators
- Specific cost/revenue figures
- Named tools with specific capabilities
- Real benchmark numbers
- "I did X in Y time" format
- Architecture decisions with tradeoffs
- Founder decisions with consequences

### Reject These
- Vague announcements ("X launches new AI feature")
- Hot takes with no data
- Already-covered territory (if 3 similar stories in DB, skip)
- Non-builder topics (pure politics, pure hype)

---

## Story Freshness Rules

| Story Type | Max Age | Notes |
|------------|---------|-------|
| Tool launches | 7 days | Fresh = more credible |
| Benchmarks | 14 days | Still relevant if methodology is sound |
| Architecture posts | 30 days | Evergreen, timeless patterns |
| "I built X" stories | 30 days | Outcome still relevant |
| Opinion pieces | 7 days | timeliness matters |

---

## How to Select Stories for Generation

1. **Check pending stories** — `get_unprocessed_stories()` ordered by points
2. **Filter by relevance** — skip if not in Dusk's focus areas
3. **Check recency** — reject if too old for type
4. **Pre-check for duplicates** — skip if similar story already used in last 7 days
5. **Pick top 3** — highest points that pass filters

---

## Story Enrichment

Before generating, enrich the story with:
- Source reputation (HN > Reddit > X for technical credibility)
- Engagement context (points, comments — tells you what resonated)
- Your angle — what's the specific take this story enables?

---

## When to Refresh the Brain

- Story fetch cron: **8 AM daily** — new stories from HN, relevant subreddits
- Manual refresh: when DB has <20 unprocessed stories, fetch more
- Never let the brain go stale — content quality depends on story quality

---

## Pitfalls

1. **Using old stories** — posts about "breaking news" from 2 weeks ago look silly
2. **Forcing relevance** — stretching a story to fit a pillar dilutes the content
3. **Ignoring engagement signals** — high-point stories on HN already validated what resonated
4. **Duplicate angles** — check what you've posted recently, don't repeat the same take

---

## Procedure

1. Run `get_unprocessed_stories(limit=20)` from prism_db
2. Filter each story against Selection Criteria
3. Filter by freshness rules
4. Filter for duplicates (title similarity or same topic in last 7 days)
5. Pick top 3 that pass all filters
6. Pass to x_writer for generation

---

## Verification

To verify the brain is healthy:
1. Run `python3 run.py status` — should show 20+ stories, <10 pending drafts
2. Run `fetch` command — new stories should appear
3. Check stories table has variety of sources (HN, Reddit, X)
