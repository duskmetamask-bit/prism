"""
PRISM Content Brain
Decides WHAT to post: topic + hook type + content brief

Usage:
    from content_brain import generate_brief
    brief = generate_brief(topic="AI agents for tradies")
"""

import json
import random
import sqlite3
import yaml
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "database" / "prism.db"
CONFIG_PATH = BASE_DIR / "config" / "user-profile.yaml"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"


def load_user_profile():
    """Load user profile from YAML."""
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)


def load_db():
    """Connect to SQLite database."""
    return sqlite3.connect(DB_PATH)


def get_top_hooks(conn, limit=3):
    """Get top performing hooks from content bank."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT hook_type, hook_formula,
               (times_hit * 1.0 / NULLIF(times_used, 0)) as hit_rate,
               times_used
        FROM hooks
        WHERE times_used > 0
        ORDER BY hit_rate DESC, times_used DESC
        LIMIT ?
    """, (limit,))
    return cursor.fetchall()


def get_random_hook(conn, preferred_types=None):
    """Get a hook, preferring types that have performed well."""
    cursor = conn.cursor()

    # Try top hooks first if we have any data
    top = get_top_hooks(conn, 3)
    if top and random.random() < 0.6:  # 60% chance to use a proven hook
        hook = random.choice(top)
        return {
            "hook_type": hook[0],
            "hook_formula": hook[1],
            "source": "content_bank"
        }

    # Otherwise pick from all hooks, weighted toward variety
    cursor.execute("SELECT hook_type, hook_formula FROM hooks ORDER BY RANDOM() LIMIT 1")
    row = cursor.fetchone()
    return {
        "hook_type": row[0],
        "hook_formula": row[1],
        "source": "library"
    }


def get_topic(conn, user_profile):
    """Pick a topic from user's topics, considering what we've posted recently."""
    cursor = conn.cursor()

    # Get topics we've posted recently (last 7 days)
    cursor.execute("""
        SELECT topic, COUNT(*) as count
        FROM posts
        WHERE created_at > datetime('now', '-7 days')
        GROUP BY topic
    """)
    recent = {row[0]: row[1] for row in cursor.fetchall()}

    # Get all user topics
    user_topics = user_profile.get('topics', [])

    # Also add current topics
    current = user_profile.get('current_topics', [])
    all_topics = user_topics + current

    # Filter out anything posted in last 3 days
    available = [t for t in all_topics if recent.get(t, 0) < 2]

    if not available:
        available = all_topics  # Reset if everything was recently posted

    return random.choice(available)


def generate_brief(topic=None, platform="X"):
    """
    Generate a content brief for the week.

    Returns:
        dict with topic, hook_type, hook_formula, platform, format, key_message
    """
    user = load_user_profile()
    conn = load_db()

    # Pick topic
    if not topic:
        topic = get_topic(conn, user)

    # Pick hook
    hook = get_random_hook(conn)

    # Determine format based on platform
    format_map = {
        "X": random.choice(["thread-5", "thread-7", "single"]),
        "LinkedIn": random.choice(["post", "carousel"]),
        "Newsletter": "email"
    }
    content_format = format_map.get(platform, "thread-5")

    conn.close()

    # Build the brief
    brief = {
        "topic": topic,
        "hook_type": hook["hook_type"],
        "hook_formula": hook["hook_formula"],
        "hook_source": hook["source"],
        "platform": platform,
        "format": content_format,
        "voice_reminder": {
            "style": user["voice"]["style"].strip(),
            "tone": user["voice"]["tone"].strip(),
            "avoids": user["voice"]["avoids"]
        },
        "cta_style": user["goals"]["call_to_action_style"].strip(),
        "target_audience": user["goals"]["target_audience"].strip(),
        "generated_at": datetime.now().isoformat()
    }

    return brief


def save_draft_to_db(brief, content, status="pending"):
    """Save a generated draft to the database."""
    conn = load_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO drafts (topic, hook_type, hook_formula, platform, format, content, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        brief["topic"],
        brief["hook_type"],
        brief["hook_formula"],
        brief["platform"],
        brief["format"],
        json.dumps(content),
        status
    ))

    draft_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return draft_id


def get_pending_drafts():
    """Get all drafts waiting for review."""
    conn = load_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, topic, hook_type, platform, format, content, created_at
        FROM drafts
        WHERE status = 'pending'
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    drafts = []
    for row in rows:
        drafts.append({
            "id": row[0],
            "topic": row[1],
            "hook_type": row[2],
            "platform": row[3],
            "format": row[4],
            "content": json.loads(row[5]),
            "created_at": row[6]
        })
    return drafts


if __name__ == "__main__":
    # Test: generate a brief
    brief = generate_brief()
    print(json.dumps(brief, indent=2))
