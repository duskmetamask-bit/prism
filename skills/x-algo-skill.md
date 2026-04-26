# X Algorithm Skill
**For:** PRISM content agent
**Purpose:** Encode X algorithm rules so PRISM writes posts that the algorithm rewards
**Last updated:** 2026-04-25

---

## Core Rule: What the Algorithm Rewards

X algorithm's primary signal is **engagement velocity in the first 2 hours**. Everything below serves that goal.

### What the Algorithm Surfaces
- Posts with fast early engagement (likes + replies + reposts in first 30-60 min)
- **Replies with commentary** — conversations in replies boost reach significantly
- **Quote tweets with original commentary** > plain retweets
- **Saves/bookmarks** — strong quality signal
- Fresh followers gained from a post
- High follower-to-impression ratio

### What the Algorithm Suppresses
- **Link posts** — algorithm suppresses posts with links vs. text-only
- Excessive @mentions or #hashtags
- Low engagement in first 2 hours (algo kills it fast)
- **Frequent posting** — flood penalty, "spammy" signal
- Low reply rate — algorithm wants conversation, not broadcast

---

## Golden Rule: Text-Only Posts

**Every post should be text-only unless there's a specific reason to add an image.**

Why: Link posts get suppressed. Image posts compete with millions of images. Text posts from an account with engagement history can out-perform both.

If posting a link: put the insight in the text, not in the link preview. The link is supplementary.

---

## Optimal Post Format

### Length
- **Under 280 characters** is safest — fits all feeds, no truncation
- **280-400** is acceptable if every character earns it
- **Never** post threads as first approach — only use threads if the insight genuinely requires it

### Structure (one post)
```
[HOOK — Line 1]        ← Stop the scroll. Controversial, specific, or pattern-interrupting.
[CONTEXT — Line 2]    ← Brief setup. What is this about.
[INSIGHT — Line 3]    ← The actual value. What do they learn or what changes.
[CTA — Line 4]        ← Engagement prompt. Question, "drop your take", agree/disagree.
```

### Hook Formulas That Work on X
1. **Controversial claim** — "X is dead and here's why"
2. **Specific number** — "$0.003/call. 500 calls. Real cost of voice AI."
3. **Pattern interrupt** — "Everyone is wrong about Y"
4. **Second-person recognition** — "You don't need X, you need Y"
5. **Story micro** — "I almost quit last Tuesday. Then I found..."
6. **Contrarian reframe** — "Everyone says [common belief]. They're wrong because..."

### CTAs That Drive Replies
- "Drop your take below."
- "Agree or disagree?"
- "What's your experience been?"
- "I've been wrong about this — change my mind."
- Never: "Like if you agree" (that's engagement bait and algorithm penalises it)

---

## Timing Rules

### Optimal Windows (AWST)
| Day | Best Times |
|-----|-----------|
| Monday | 7-9am, 12-1pm, 5-6pm |
| Tuesday | 7-9am, 12pm, 5-7pm |
| Wednesday | 7-9am, 12pm, 5-6pm |
| Thursday | 7-9am, 12pm, 5-7pm (**peak day**) |
| Friday | 7-9am, 12pm |
| Saturday | 8-10am only |
| Sunday | 9-11am only |

### Flooding Rules
- **Minimum 2 hours between posts** — flooding triggers spam penalty
- **Maximum 3-5 posts per day** — more than this and algo starts throttling
- After a high-engagement post: **wait 3-4 hours** before posting again (let algo distribute)

---

## Hashtag Rules
- **1-3 hashtags maximum**
- **Never in the hook line** — kills the pattern interrupt
- Only if genuinely relevant to the topic
- More than 3 = diminishing returns, starts looking like spam

---

## What NOT To Do
- ❌ "Like if you agree" / "Retweet if..." (engagement bait — algorithm penalty)
- ❌ Threads by default (use only if insight genuinely needs expansion)
- ❌ Posting links without context in the text
- ❌ More than 3 posts in 2 hours
- ❌ @mentioning brands or people without reason
- ❌ Burying the insight behind a "read more"

---

## When You're Unsure
Default to: **one sharp, specific, text-only post under 280 chars with a clear opinion.**

If you can't make it work in one post, consider whether it needs to be a thread at all — or whether the insight isn't sharp enough yet.

---

*Update this skill when X changes its algorithm. PRISM loads this at write time.*


## Pitfalls

1. **Using threads when a single post is enough** — threads suppress individual post reach. Only use when the insight genuinely requires expansion.
2. **Editing posts after posting** — editing resets the engagement clock and kills early velocity.
3. **Posting during low-engagement windows** — AWST evening posts (6pm+) often go nowhere because US is asleep.
4. **Adding links for links' sake** — every link suppresses reach. Only include if the insight genuinely needs the link.
5. **Hashtags in the hook** — #hashtags in line 1 kill the pattern interrupt before it lands.
6. **"Like if you agree" CTA** — engagement bait, algorithm penalty, don't do it.

---

## Procedure

Follow this sequence every time you write a post:

1. **Pick a story** — select from the story brain (database/prism.db). Prefer fresh stories with specific numbers or outcomes.
2. **Identify the hook** — what pattern interrupt will stop the scroll? Choose from: controversial claim, specific number, pattern interrupt, second-person recognition, story micro, or contrarian reframe.
3. **Write the hook line** — must be under 280 chars. No hashtags. No links. Sharp and specific.
4. **Add context** — 1-2 lines of setup. What is this. Keep it tight.
5. **Deliver the insight** — what did you learn or what changes for the reader?
6. **Add a CTA** — end with a question. "Drop your take", "agree or disagree?", "what's your experience?" Never: "like if you agree."
7. **Count characters** — must be under 280 for maximum distribution. 280-400 only if every character earns it.
8. **Check hashtags** — 0-3 hashtags max. Never in the hook line.
9. **Verify no links** — unless the link is the insight itself.
10. **Save to drafts** — write to database/prism_db via insert_draft() with status='draft'. Do NOT post directly.

---



## Verification

To verify this skill is working correctly:
1. Generate a post — run `python3 run.py generate 1` and check the output is under 280 chars
2. Check the hook follows one of the 6 hook formulas in this skill
3. Check there are no links in text-only posts
4. Check CTA is a question or engagement prompt, not "like if you agree"
5. Check no hashtags in the first line
6. Check minimum 2 hours between multiple posts

---

