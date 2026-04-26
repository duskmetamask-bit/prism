"""
PRISM X Writer — Generates X/Twitter posts using LLM
Takes a story → selects angle → generates 3 posts → saves best to drafts
Uses NVIDIA NIM: google/gemma-3-27b-it
"""
import json
import os
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from database.prism_db import get_db, insert_draft, get_random_hook, mark_story_processed

# ─── LLM Client ────────────────────────────────────────────────────────────────

def get_llm_client():
    """Create NVIDIA NIM client (OpenAI-compatible)."""
    from openai import OpenAI
    # Try environment first, then read from ~/.hermes/.env directly
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        env_file = Path.home() / ".hermes" / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("NVIDIA_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )


# ─── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are writing X/Twitter posts for DuskWun — builder, AI agent developer, "Shut Up and Build" brand.

BRAND VOICE:
- Direct. States things as true. No hedging, no "I think".
- Specific. Real numbers, real tools, real outcomes. No vague statements.
- Builder-first. Comes from building real things, not reading about them.
- Opinionated. Has takes and states them clearly.
- Technical but accessible. Assumes audience is smart but doesn't show off.

NEVER DO:
- Fluff, corporate language, preamble ("In today's fast-paced world...")
- Hedging ("I think maybe perhaps...")
- Engagement bait ("like if you agree", "retweet if...")
- Threads as default — only use if insight genuinely needs expansion
- Links in text posts unless the link IS the insight itself
- Hashtags in the hook line
- Burying the insight behind "read more"

X ALGORITHM RULES:
- Engagement velocity in first 2 hours is the primary signal the algorithm rewards
- Text-only posts outperform link posts (link posts get suppressed)
- Minimum 2 hours between posts or flood penalty kicks in
- Algorithm suppresses: excessive hashtags, low early engagement, frequent posting
- CTAs must be questions — "agree or disagree?", "drop your take", "what's your experience?"
- Saves/bookmarks are strong quality signals — write content worth saving

FORMAT:
- Single posts: 100-280 characters for maximum distribution (280 is ceiling, not target)
- Hook first: pattern interrupt in line 1 — stop the scroll before anything else
- Structure: Hook → Context → Insight → CTA (question)
- Every post must be something Dusk would actually post under his own name
"""


# ─── Generation Prompt ─────────────────────────────────────────────────────────

def build_prompt(story: dict, hook: dict) -> str:
    """Build the generation prompt for a single story."""
    title = story.get("title", "")
    source = story.get("source", "")
    points = story.get("points", 0)
    summary = story.get("summary", "")
    url = story.get("url", "")

    hook_type = hook.get("hook_type", "Contrarian")
    hook_formula = hook.get("hook_formula", "")

    return f"""Story: {title}
Source: {source} | Points: {points}
Summary: {summary}
URL: {url}

Angle: {hook_type}
Angle formula: {hook_formula}

Write 1 X post from Dusk's perspective — the kind of post he'd write and publish right now under his own name.

Requirements:
- The hook must stop the scroll — controversial, specific, or pattern-interrupting in line 1
- Must sound like Dusk actually wrote it — direct, specific, opinionated, builder-voice
- Under 280 characters for single post
- No hashtags in the hook line
- End with a question (not "like if you agree")
- The insight must be specific — use numbers or details from the story
- No preamble, no "So...", no "Here's..."
- Post reads like a text message to someone who gets it, not a broadcast
"""


# ─── LLM Generation ────────────────────────────────────────────────────────────

def generate_posts_with_llm(story: dict, hooks: list, count: int = 3):
    """
    Generate `count` alternative posts for a story using the LLM.
    Returns list of post strings.
    """
    try:
        client = get_llm_client()
    except Exception as e:
        print(f"  ❌ LLM client error: {e}")
        return []

    # Pick a random hook type
    hook = hooks[0] if hooks else {"hook_type": "Contrarian", "hook_formula": "Everyone thinks [X]. They're wrong."}
    prompt = build_prompt(story, hook)

    posts = []
    for i in range(count):
        try:
            response = client.chat.completions.create(
                model="google/gemma-3-27b-it",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=200
            )
            post = response.choices[0].message.content.strip()
            # Strip any leading/trailing quotes if LLM wraps the post
            if post.startswith('"') and post.endswith('"'):
                post = post[1:-1]
            posts.append(post)
            print(f"  ✅ Generated option {i+1}: {post[:60]}...")
        except Exception as e:
            print(f"  ❌ Generation error (option {i+1}): {e}")

    return posts


def quality_check(post: str) -> tuple[bool, str]:
    """
    Check post quality against X algo rules.
    Returns (passes, reason).
    """
    if len(post) > 280:
        return False, f"Too long ({len(post)} chars)"
    if "like if you agree" in post.lower():
        return False, "Engagement bait detected"
    if "retweet if" in post.lower():
        return False, "Engagement bait detected"
    # Check for hashtags in first line (first 50 chars)
    first_line = post.split("\n")[0]
    if "#" in first_line[:50]:
        return False, "Hashtag in hook line"
    # Must end with a question
    stripped = post.strip()
    if not stripped.endswith("?") and not any(c in stripped for c in "?!"):
        return False, "No question CTA"
    return True, "OK"


def pick_best_post(posts: list) -> str:
    """Pick the best post from alternatives based on quality checks."""
    for post in posts:
        passes, reason = quality_check(post)
        if passes:
            return post
    # If all fail quality, return first and we'll log the issues
    return posts[0] if posts else ""


# ─── Main Entry Point ───────────────────────────────────────────────────────────

def generate_posts(count: int = 3):
    """
    Generate X posts from unprocessed stories.
    For each story: generate 3 alternatives, pick best, save to drafts.
    """
    from database.prism_db import get_unprocessed_stories

    stories = get_unprocessed_stories(limit=count)
    if not stories:
        print("📭 No pending stories")
        return 0

    hooks = get_random_hook(limit=5)
    generated = 0

    for story in stories:
        title = story.get("title", "")[:60]
        print(f"\n[*] Generating for: {title}...")

        posts = generate_posts_with_llm(story, hooks, count=3)
        if not posts:
            print(f"  ❌ No posts generated for: {title}")
            continue

        best_post = pick_best_post(posts)
        quality_passed, reason = quality_check(best_post)

        draft = {
            "story_id": story.get("id"),
            "platform": "X",
            "topic_id": "ai_agents",
            "topic_name": "AI Agent sector",
            "format": "single",
            "content": {
                "posts": posts,  # save all 3 for Dusk to choose
                "selected": best_post,
                "quality_passed": quality_passed,
                "quality_reason": reason,
                "story_title": story.get("title"),
                "story_source": story.get("source"),
                "story_url": story.get("url", ""),
                "points": story.get("points", 0)
            },
            "hook": hooks[0].get("hook_type", "Unknown") if hooks else "Unknown",
            "angle": "llm_generated",
            "status": "pending"
        }

        draft_id = insert_draft(draft)
        mark_story_processed(story.get("id"))

        if quality_passed:
            print(f"  ✅ Draft {draft_id}: {best_post[:80]}...")
        else:
            print(f"  ⚠️ Draft {draft_id} (quality issue: {reason}): {best_post[:60]}...")
        generated += 1

    return generated


def generate_pending_stories(limit: int = 3):
    """Alias for generate_posts — backward compatibility."""
    return generate_posts(count=limit)


def preview_draft(draft_id: int):
    """Print a draft for review."""
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM drafts WHERE id=?", (draft_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        print(f"Draft {draft_id} not found")
        return

    content = json.loads(row["content"])
    selected = content.get("selected", "")
    all_posts = content.get("posts", [selected])

    print(f"\n{'='*60}")
    print(f"Draft #{row['id']} | {row['platform']} | {row['status']}")
    print(f"Hook: {row['hook']} | Angle: {row['angle']}")
    print(f"{'='*60}")

    if len(all_posts) > 1:
        print("ALTERNATIVES:")
        for i, p in enumerate(all_posts):
            print(f"\n  [{i+1}] {p}")

    print(f"\nSELECTED: {selected}")
    print(f"Quality: {content.get('quality_reason', 'N/A')}")
    if content.get("story_title"):
        print(f"Story: {content['story_title'][:80]}")
    print(f"{'='*60}")


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        # Preview all pending drafts
        conn = get_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id FROM drafts WHERE status='pending' ORDER BY created_at DESC LIMIT 5")
        for row in cur.fetchall():
            preview_draft(row["id"])
        conn.close()
    else:
        count = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        generated = generate_posts(count=count)
        print(f"\n📝 Generated {generated} drafts")
