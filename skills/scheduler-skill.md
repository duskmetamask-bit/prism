# Scheduler Skill
**For:** PRISM content agent
**Purpose:** When and how to schedule posts for maximum algorithm impact
**Last updated:** 2026-04-25

---

## Core Principle

Posting at the wrong time kills content. The same post, posted at the right time, reaches 2-4x more audience. Timing is not optional — it is the execution of the content strategy.

---

## X Optimal Windows (AWST)

| Day | Best Times | Peak | Notes |
|-----|-----------|------|-------|
| Monday | 7-9am, 12-1pm, 5-6pm | 8am | Week starts slow, mid-morning pickup |
| Tuesday | 7-9am, 12pm, 5-7pm | 12pm | Strong all day |
| Wednesday | 7-9am, 12pm, 5-6pm | 12pm | Consistent mid-week |
| Thursday | 7-9am, 12pm, 5-7pm | 7pm | **Peak day** — highest engagement |
| Friday | 7-9am, 12pm | 8am | Week fatigue sets in, afternoon dies |
| Saturday | 8-10am only | 9am | Low volume = less competition |
| Sunday | 9-11am only | 10am | Niche audience, dedicated readers |

---

## Flood Rules

- **Minimum 2 hours between posts** — flooding triggers spam penalty
- **Maximum 3-5 posts per day** — algo starts throttling after 5
- **After high-engagement post: wait 3-4 hours** — let algo distribute before next post
- **Never post during dead windows** — late night (8pm+) AWST = US sleep = near-zero early engagement

---

## Optimal Cadence

- **3 posts/day** on peak days (Tue-Thu) — maximize reach while avoiding flood penalty
- **1-2 posts/day** on low days (Fri-Sun) — maintain presence without wasting posts
- **Monday** — 2 posts, ease into the week

---

## Day Strategy

| Day | Cadence | Strategy |
|-----|---------|----------|
| Monday | 2 posts | Educational + engagement prompt |
| Tuesday | 3 posts | Mix: story, opinion, tool deep dive |
| Wednesday | 3 posts | Mix: contrarian, architecture, numbers |
| Thursday | 3 posts | Peak day — save best content for this |
| Friday | 1-2 posts | Light — avoid low-engagement afternoon |
| Saturday | 1 post | One strong piece only |
| Sunday | 1 post | One strong piece only |

---

## Queue Management

When scheduling drafts for review:
1. Pull pending drafts from `drafts` table
2. Assign optimal posting window based on day and existing queue
3. Add `scheduled_time` field to draft record
4. Output: draft with recommended posting time for human approval

---

## When to Escalate to Human

PRISM never schedules — it recommends. Human reviews and approves before anything goes out.

Dusk gets:
- Draft content
- Recommended posting time
- Source/story reference
- Hook type and angle

Dusk approves → content is queued for posting.

---

## Pitfalls

1. **Posting during dead windows** — AWST evening (6pm+) posts die because US is asleep
2. **Flooding** — 4+ posts in 2 hours triggers spam penalty, tanks reach
3. **Back-to-back posts** — no gap between posts = algo flags as spam
4. **Sunday evening posting** — lowest engagement of the week
5. **Friday afternoon** — week fatigue, engagement drops sharply after 2pm

---

## Procedure

1. After generating draft(s), check current queue — what time is the last post going out today?
2. Apply flood rules — minimum 2 hour gap
3. Assign recommended window based on day strategy above
4. Save recommendation with draft
5. Present to human (MEWY → Dusk) for approval

---

## Verification

1. Check scheduling recommendation matches day strategy above
2. Confirm no flood violations (2hr minimum between posts)
3. Confirm posts land in optimal windows, not dead windows
