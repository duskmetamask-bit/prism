"""
PRISM X Writer — LLM-Powered
Writes X/Twitter content using MiniMax for actual copy generation.

Usage:
    from x_writer import write_x_thread
    thread = write_x_thread(brief)
"""

import json
import random
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "user-profile.yaml"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"

X_MAX_CHARS = 280
MAX_HASHTAGS = 2


def load_user_profile():
    """Load user profile YAML."""
    import yaml
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)


def get_llm_response(prompt, model="MiniMax-M2.7"):
    """Call MiniMax API directly."""
    import urllib.request
    import urllib.error
    import os

    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        # Load from ~/.openclaw/.env
        env_file = os.path.expanduser("~/.openclaw/.env")
        if os.path.exists(env_file):
            for line in open(env_file):
                if line.startswith("MINIMAX_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8
    }

    try:
        req = urllib.request.Request(
            "https://api.minimax.io/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[LLM ERROR: {e}]"


def generate_hook_tweet(topic, hook_type, user_profile):
    """Generate the HOOK tweet (tweet 1) using LLM."""
    voice = user_profile["voice"]
    audience = user_profile["goals"]["target_audience"].split("\n")[0].strip()

    prompt = f"""You are writing the FIRST tweet (hook) for a X/Twitter thread.

CONTEXT:
- Topic: {topic}
- Hook type: {hook_type}
- Target audience: {audience}

VOICE (write EXACTLY like this person):
{voice['style']}
{voice['tone']}

WHAT TO AVOID:
{chr(10).join(['- ' + a for a in voice['avoids']])}

RULES:
- Must stop the scroll in 3 seconds (curiosity gap, bold claim, or specific number)
- Maximum {X_MAX_CHARS} characters
- NO hashtags in the main tweet (links go in reply)
- Must be SPECIFIC not generic — use real numbers, real situations
- Must SOUND like a real human, not AI

Write the HOOK tweet (first tweet only). Start immediately with the hook.
Output just the tweet text, nothing else."""

    result = get_llm_response(prompt)
    # Strip any quotes wrapper
    result = result.strip().strip('"').strip("'")
    return result


def generate_thread_tweet(topic, tweet_number, total_tweets, context, user_profile):
    """Generate a subsequent tweet in the thread using LLM."""

    voice = user_profile["voice"]

    prompt = f"""You are writing tweet {tweet_number} of {total_tweets} in a X/Twitter thread.

TOPIC: {topic}
CONTEXT FROM PREVIOUS TWEETS: {context}

VOICE:
{voice['style']}
{voice['tone']}

WHAT TO AVOID:
{chr(10).join(['- ' + a for a in voice['avoids']])}

RULES:
- Maximum {X_MAX_CHARS} characters
- NO hashtags (or max {MAX_HASHTAGS} if absolutely needed)
- Must be SPECIFIC — real examples, real numbers, real situations
- Must advance the argument/story
- Each tweet must stand alone (don't reference "as I mentioned")
- Keep momentum — don't restate, build

Output just the tweet text, nothing else."""

    result = get_llm_response(prompt)
    result = result.strip().strip('"').strip("'")
    return result


def generate_cta_tweet(topic, hook_type, user_profile):
    """Generate the closing CTA tweet."""
    voice = user_profile["voice"]
    cta_style = user_profile["goals"]["call_to_action_style"]

    prompt = f"""You are writing the FINAL tweet of a X/Twitter thread.

TOPIC: {topic}
HOOK TYPE: {hook_type}

VOICE:
{voice['style']}

WHAT TO AVOID:
{chr(10).join(['- ' + a for a in voice['avoids']])}

The user's preferred CTA style:
{cta_style}

RULES:
- Maximum {X_MAX_CHARS} characters
- This should drive REPLIES (ask a question, get a perspective, invite disagreement)
- Or: "Save this if you know someone who..."
- Don't say "follow for more" — it's weak
- End with the CTA naturally

Output just the tweet text."""

    result = get_llm_response(prompt)
    result = result.strip().strip('"').strip("'")
    return result


def build_thread_structure(hook_type):
    """Define how many tweets and what each does based on hook type."""
    structures = {
        "counterintuitive": {
            "count": 6,
            "flow": ["hook", "context", "evidence", "proof", "action", "cta"]
        },
        "specificity": {
            "count": 6,
            "flow": ["hook", "context", "insight", "proof", "action", "cta"]
        },
        "story": {
            "count": 6,
            "flow": ["hook", "context", "struggle", "turning", "result", "cta"]
        },
        "authority": {
            "count": 6,
            "flow": ["hook", "claim", "point_1", "point_2", "point_3", "cta"]
        },
        "lessons": {
            "count": 6,
            "flow": ["hook", "lesson_1", "lesson_2", "lesson_3", "lesson_4", "cta"]
        },
        "prediction": {
            "count": 6,
            "flow": ["hook", "evidence", "implication_1", "implication_2", "action", "cta"]
        },
        "default": {
            "count": 5,
            "flow": ["hook", "context", "insight", "action", "cta"]
        }
    }
    return structures.get(hook_type, structures["default"])


def enforce_limits(text):
    """Ensure tweet is under X limits."""
    # Truncate if over
    if len(text) > X_MAX_CHARS:
        text = text[:X_MAX_CHARS - 3] + "..."

    # Remove any URLs
    text = re.sub(r'https?://\S+', '', text)

    # Clean whitespace
    text = re.sub(r'  +', ' ', text).strip()

    return text


def write_x_thread(brief):
    """
    Main function: write a X thread from a content brief.
    Uses LLM to generate actual copy.

    Returns:
        {
            "tweets": [{"number": 1, "text": "...", "is_hook": True}, ...],
            "meta": {...}
        }
    """
    user = load_user_profile()
    topic = brief["topic"]
    hook_type = brief["hook_type"]

    structure = build_thread_structure(hook_type)
    num_tweets = structure["count"]

    tweets = []
    context = ""  # For LLM context window

    # Tweet 1: The Hook (always generated first with full context)
    hook_text = generate_hook_tweet(topic, hook_type, user)
    hook_text = enforce_limits(hook_text)

    tweets.append({
        "number": 1,
        "type": "hook",
        "text": hook_text,
        "is_hook": True,
        "char_count": len(hook_text)
    })

    context = f"Tweet 1: {hook_text}"

    # Tweets 2 to N-1: Build the thread
    for i in range(2, num_tweets):
        tweet_text = generate_thread_tweet(
            topic=topic,
            tweet_number=i,
            total_tweets=num_tweets,
            context=context,
            user_profile=user
        )
        tweet_text = enforce_limits(tweet_text)

        tweets.append({
            "number": i,
            "type": structure["flow"][i - 1],
            "text": tweet_text,
            "is_hook": False,
            "char_count": len(tweet_text)
        })

        context += f"\nTweet {i}: {tweet_text}"

    # Final tweet: CTA
    cta_text = generate_cta_tweet(topic, hook_type, user)
    cta_text = enforce_limits(cta_text)

    tweets.append({
        "number": num_tweets,
        "type": "cta",
        "text": cta_text,
        "is_hook": False,
        "char_count": len(cta_text)
    })

    meta = {
        "topic": topic,
        "hook_type": hook_type,
        "hook_formula": brief["hook_formula"],
        "platform": "X",
        "format": brief["format"],
        "voice_used": {
            "style": user["voice"]["style"][:80] + "...",
            "tone": user["voice"]["tone"][:80] + "..."
        },
        "total_tweets": len(tweets),
        "generated_at": datetime.now().isoformat()
    }

    return {
        "tweets": tweets,
        "meta": meta
    }


def format_for_review(thread_output):
    """Format thread for human review (Telegram-friendly)."""
    lines = []
    lines.append("🧵 THREAD DRAFT")
    lines.append("=" * 40)
    lines.append(f"Topic: {thread_output['meta']['topic']}")
    lines.append(f"Hook: {thread_output['meta']['hook_type']} | Tweets: {thread_output['meta']['total_tweets']}")
    lines.append("=" * 40)
    lines.append("")

    for tweet in thread_output["tweets"]:
        prefix = "⬜ HOOK" if tweet["is_hook"] else f"   Tweet {tweet['number']}"
        lines.append(f"{prefix} ({tweet['char_count']} chars)")
        lines.append(tweet["text"])
        lines.append("")

    lines.append("=" * 40)
    lines.append("POSTING RULES:")
    lines.append("- HOOK tweet: Link goes in FIRST REPLY")
    lines.append("- Subsequent tweets: No links")
    lines.append("- Schedule at: 9am / 12pm / 6pm AWST")
    lines.append("")
    lines.append("COMPOSE: https://x.com/compose/tweet")

    return "\n".join(lines)


if __name__ == "__main__":
    # Test
    import sys
    sys.path.insert(0, str(BASE_DIR / "engine"))
    from content_brain import generate_brief

    brief = generate_brief(topic="AI agents for tradies")
    print(f"Generating thread: {brief['topic']} ({brief['hook_type']})...")

    thread = write_x_thread(brief)
    print(format_for_review(thread))
