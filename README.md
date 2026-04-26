# PRISM — Content Intelligence Agent

**What it does:** Generates X posts from the story brain. Takes research + stories, applies the X algorithm, outputs draft posts ready for publishing.

**Owner:** MEWY  
**Platform:** Hermes CLI  
**Location:** `~/.hermes/agents/prism/`

---

## Commands

```bash
cd ~/.hermes/agents/prism

python3 run.py generate [count]   # Generate N X posts from story brain
python3 run.py status             # Show story count, drafts, queue
python3 run.py fetch              # Fetch fresh stories from sources
```

---

## Architecture

```
prism/
├── SOUL.md                    ← Identity
├── SPEC.md                    ← Architecture
├── run.py                     ← CLI entry point
├── skills/
│   └── x-algo-skill.md       ← X algorithm rules (loaded at write time)
├── database/
│   ├── prism_db.py           ← SQLite interface
│   └── prism.db              ← Story brain + drafts
├── writers/
│   └── x_writer.py           ← X post generator
├── scripts/
│   └── fetch_stories.py      ← Story fetcher
└── drafts/                    ← Draft posts (text files)
```

---

## How It Works

1. Stories are fetched from sources → stored in `prism.db` (story brain)
2. When generating: picks a story → applies x-algo-skill rules → writes post → saves to drafts
3. Dusk reviews drafts → approves/edits → publishes manually

**PRISM does NOT auto-post. All output goes to drafts first.**

---

## X Algorithm Rules (Summary)

- Text-only posts outperform link posts
- Under 280 chars safest
- Hook must stop the scroll — no generic statements
- End with a question (drives replies = algorithm reward)
- Minimum 2 hours between posts
- No engagement bait ("like if you agree")
- Optimal windows: AWST 7-9am, 12pm, 5-7pm (Thu is peak day)

---

## Status

Currently: **PAUSED** — needs review before first post.

Cron: PRISM Daily Story Fetch runs at 8 AM daily (story fetching only — no auto-post).
