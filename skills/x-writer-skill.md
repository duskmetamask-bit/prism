# X Writer Skill
**For:** PRISM content agent
**Purpose:** How to use the LLM to write actual X posts — not template filling, real generation
**Last updated:** 2026-04-25

---

## Core Capability

PRISM uses the NVIDIA NIM LLM (`google/gemma-3-27b-it`) to write X posts. The LLM receives:
- The story to write about
- The x-algo-skill rules
- Dusk's voice profile
- The angle/hook type

The LLM generates original posts. Templates are reference material, not filling instructions.

---

## LLM Setup

**Provider:** NVIDIA NIM (OpenAI-compatible API)
**Base URL:** `https://integrate.api.nvidia.com/v1`
**Model:** `google/gemma-3-27b-it`
**API Key:** from `~/.hermes/.env` → `NVIDIA_API_KEY`

```python
import openai
client = openai.OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)
```

---

## System Prompt

The LLM is given Dusk's voice and platform rules. Write this as the system prompt:

```
You are writing X/Twitter posts for DuskWun — builder, AI agent developer, "Shut Up and Build" brand.

BRAND VOICE:
- Direct. States things as true. No hedging.
- Specific. Real numbers, real tools, real outcomes. No vague.
- Builder-first. Comes from building real things, not reading about them.
- Opinionated. Has takes and states them.
- Technical but accessible. Assumes audience is smart but doesn't show off.

NEVER:
- Fluff, corporate language, preamble
- "I think", "maybe", "perhaps"
- Engagement bait ("like if you agree")
- Threads as default (only if insight genuinely needs expansion)
- Links in text posts (unless the link IS the insight)
- Hashtags in the hook line

X ALGO RULES (know these):
- Engagement velocity in first 2 hours is the primary signal
- Text-only posts outperform link posts
- Flood penalty: min 2 hours between posts
- Algorithm suppresses: excessive hashtags, low early engagement, frequent posting
- CTAs must be questions, not "like if you agree"

FORMAT:
- Single posts: 100-280 characters for maximum distribution
- Threads: only when insight genuinely requires expansion
- Hook first: pattern interrupt in line 1
- Structure: Hook → Context → Insight → CTA (question)
```

---

## Per-Post Generation Prompt

Generate one post per story. Use this template:

```
Story: {title}
Source: {source} | Points: {points}
Summary: {summary}

Angle: {selected_hook_type}
Angle description: {hook_formula}

Write 1 X post from Dusk's perspective. 

Requirements:
- The hook must stop the scroll — controversial, specific, or pattern-interrupting
- Must sound like Dusk actually wrote it — direct, specific, opinionated
- Under 280 characters for single post
- No hashtags in the hook line
- End with a question (not "like if you agree")
- The insight must be specific — not generic advice
- Source attribution optional for single posts
```

---

## Multi-Post Generation

Generate 3 alternatives per story, then pick the best one:

```python
# Generate 3 alternatives
alternatives = []
for i in range(3):
    response = client.chat.completions.create(
        model="google/gemma-3-27b-it",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": PER_POST_PROMPT}
        ],
        temperature=0.9,  # creative but not unhinged
        max_tokens=200
    )
    alternatives.append(response.choices[0].message.content.strip())
```

Save all 3 to drafts. Let Dusk pick.

---

## Hook Quality Checklist

Before saving draft, verify:
- [ ] Under 280 chars (single post)
- [ ] Hook is in line 1 (no preamble before the hook)
- [ ] No hashtags in hook line
- [ ] No links in text-only post
- [ ] CTA is a question
- [ ] No engagement bait ("like if you agree")
- [ ] Sounds like Dusk (read it out loud)

---

## Pitfalls

1. **Template-following** — the LLM should be generating, not filling templates. If the output looks like template rearrangement, increase temperature and re-prompt.
2. **Generic output** — if posts come out vague, add "be specific, use the numbers from the story" to the prompt
3. **Out of character** — if voice drifts corporate, the system prompt isn't strong enough. Reinforce with "you sound like a builder talking to other builders, not a brand talking to customers"
4. **Too long** — enforce character count strictly. 280 is the ceiling, not the target.

---

## Output

Save to drafts with:
- Full post text
- Hook type
- Angle
- Recommended posting window (from scheduler-skill)
- Source reference

Never post directly. All output → drafts for human review.

---

## Verification

1. Generate 3 posts for 1 story
2. Check all pass Hook Quality Checklist
3. Check all under 280 chars
4. Check all sound like Dusk (not corporate, not generic AI)
5. Check all have question CTAs
