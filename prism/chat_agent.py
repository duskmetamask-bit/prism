"""
PRISM Chat Agent — Conversational interface for social content strategy
Connects to NVIDIA NIM LLM, uses PRISM database as memory
"""
import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))
from database.prism_db import (
    get_db, get_user_profile, set_user_profile,
    log_improvement, get_improvements,
    add_calendar_entry, get_calendar, get_pillar_coverage,
    get_pending_drafts, get_topics
)

# ─── LLM Client ────────────────────────────────────────────────────────────────

def get_llm_client():
    from openai import OpenAI
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

# ─── System Prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are PRISM — Dusk's AI social content agent. Your job is to help him grow his social capital through strategic, high-quality content.

You have access to:
- User profile (goals, pillars, voice, style)
- Content improvements log
- Content calendar
- Pending drafts
- Topic/pillar database

You help with:
1. Content strategy — what to post, when, about what
2. Profile optimization — bio, pinned, positioning
3. Post feedback — what works, what doesn't
4. Chat-based content generation — write posts on demand
5. Gap detection — what pillars are stale, what needs coverage
6. Improvement tracking — log what works, what doesn't

BRAND VOICE you enforce:
- Direct. States things as true. No hedging.
- Specific. Real numbers, real tools, real outcomes.
- Builder-first. Comes from building, not reading.
- Opinionated. Has takes and states them clearly.
- Technical but accessible.

Never:
- Engagement bait ("like if you agree", "retweet if...")
- Fluff or corporate language
- Hedging ("I think maybe perhaps...")
- Burying the insight

When Dusk tells you something about his preferences, style, or strategy — log it as an improvement automatically.

When asked what's missing or what needs attention — check the pillar coverage and highlight gaps.

Be concise. Be useful. Be direct."""


# ─── Profile Management ─────────────────────────────────────────────────────────

DEFAULT_PILLARS = [
    "AI Agents",
    "OpenClaw",
    "Hermes",
    "AI Model Updates",
    "Workflows & Automations",
    "Agents You Build",
    "Setups & How-Tos",
    "Educational",
    "Tips & Tricks",
]

def ensure_profile():
    """Ensure a profile exists. Returns current profile."""
    profile = get_user_profile()
    if not profile:
        # Create default profile — Dusk fills in the rest
        set_user_profile({
            "name": "Dusk",
            "x_handle": "@duskunzzz",
            "bio": "",
            "focus_areas": [],
            "content_pillars": DEFAULT_PILLARS,
            "voice_style": "direct, specific, builder-first, opinionated",
            "voice_tone": "confident, no hedging",
            "voice_avoids": ["fluff", "engagement bait", "hedging"],
            "platforms": ["X"],
            "posting_cadence": "daily",
            "posting_windows": [],
            "unique_take": "",
            "goals": "build social capital in AI agent space",
            "target_audience": "builders, developers, AI enthusiasts",
            "follower_count": 0
        })
        return get_user_profile()
    return profile

def update_profile_field(field: str, value):
    """Update a single profile field."""
    profile = ensure_profile()
    profile[field] = value
    set_user_profile(profile)
    return profile

# ─── Chat Handler ─────────────────────────────────────────────────────────────

def build_context(profile, improvements, calendar, pillars_status):
    """Build the context block for the LLM."""
    pillars = profile.get('content_pillars', DEFAULT_PILLARS)
    pillar_list = "\n".join([f"- {p}" for p in pillars])
    
    recent_improvements = improvements[:10]
    improvements_text = "\n".join([
        f"- [{i['category']}] {i['change_type']}: {i['description']}"
        for i in recent_improvements
    ]) if recent_improvements else "No improvements logged yet."
    
    upcoming = calendar[:7]
    calendar_text = "\n".join([
        f"- {c['planned_date']}: {c['pillar']} / {c.get('topic', 'TBD')} [{c['status']}]"
        for c in upcoming
    ]) if upcoming else "No calendar entries yet."
    
    pillar_text = "\n".join([
        f"- {p['pillar']}: last posted {p['last_date'] or 'never'} ({p['total']} entries)"
        for p in pillars_status
    ]) if pillars_status else f"- All pillars: {pillar_list}"
    
    return f"""CURRENT USER PROFILE:
- Name: {profile.get('name', 'Dusk')}
- X handle: {profile.get('x_handle', '@duskunzzz')}
- Bio: {profile.get('bio', 'Not set')}
- Goals: {profile.get('goals', 'Not set')}
- Target audience: {profile.get('target_audience', 'Not set')}
- Posting cadence: {profile.get('posting_cadence', 'Not set')}
- Follower count: {profile.get('follower_count', 0)}

CONTENT PILLARS ({len(pillars)}):
{pillar_list}

PILLAR COVERAGE (stale = needs attention):
{pillar_text}

UPCOMING CALENDAR (next 7 days):
{calendar_text}

RECENT IMPROVEMENTS (agent learnings):
{improvements_text}
"""


def chat(message: str, profile=None, improvements=None, calendar=None, pillars_status=None):
    """
    Main chat function. Takes a message, returns a response.
    All context must be passed in (DB queries done at API layer).
    """
    try:
        client = get_llm_client()
    except Exception as e:
        return f"❌ LLM error: {e}"

    profile = profile or ensure_profile()
    improvements = improvements or get_improvements(limit=20)
    calendar = calendar or get_calendar(limit=7)
    
    # Get pillar coverage
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT pillar, MAX(planned_date) as last_date, COUNT(*) as total
        FROM content_calendar WHERE status IN ('planned','posted') GROUP BY pillar
    """)
    pillars_status = [dict(r) for r in cur.fetchall()]
    conn.close()
    
    # Add missing pillars with "never"
    all_pillars = profile.get('content_pillars', DEFAULT_PILLARS)
    covered_pillars = {p['pillar'] for p in pillars_status}
    for p in all_pillars:
        if p not in covered_pillars:
            pillars_status.append({'pillar': p, 'last_date': None, 'total': 0})
    pillars_status.sort(key=lambda x: x['last_date'] or '')

    context = build_context(profile, improvements, calendar, pillars_status)
    
    try:
        response = client.chat.completions.create(
            model="google/gemma-3-27b-it",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + "\n\nCONTEXT:\n" + context},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {e}"


def auto_log_improvement(category: str, change_type: str, description: str, impact: int = 5):
    """Automatically log an improvement from a conversation."""
    log_improvement({
        "category": category,
        "change_type": change_type,
        "description": description,
        "impact_score": impact,
        "source": "chat"
    })

# ─── Profile Setup Questions ───────────────────────────────────────────────────

SETUP_QUESTIONS = [
    ("What do you want to be known for?", "goals"),
    ("Who's your target audience?", "target_audience"),
    ("What's your current follower count?", "follower_count"),
    ("How often do you want to post?", "posting_cadence"),
    ("Any specific posting times that work for you?", "posting_windows"),
]

def get_next_setup_question(profile):
    """Return the next unanswered setup question."""
    for question, field in SETUP_QUESTIONS:
        val = profile.get(field)
        if field == 'follower_count' and (val is None or val == 0):
            return question, field
        if not val and field != 'follower_count':
            return question, field
    return None, None

# ─── Gap Analysis ─────────────────────────────────────────────────────────────

def get_content_gaps(profile=None, days_stale=7):
    """Return pillars that haven't been covered in `days_stale` days."""
    profile = profile or ensure_profile()
    pillars = profile.get('content_pillars', DEFAULT_PILLARS)
    
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    gaps = []
    for pillar in pillars:
        cur.execute("""
            SELECT MAX(planned_date) as last_date FROM content_calendar
            WHERE pillar=? AND status IN ('planned','posted')
        """, (pillar,))
        row = cur.fetchone()
        last = row['last_date'] if row else None
        
        if not last:
            gaps.append({"pillar": pillar, "days_ago": None, "priority": "high"})
        else:
            from datetime import datetime
            last_dt = datetime.strptime(last, "%Y-%m-%d")
            days_ago = (datetime.now() - last_dt).days
            if days_ago >= days_stale:
                gaps.append({"pillar": pillar, "days_ago": days_ago, "priority": "medium" if days_ago < 14 else "high"})
    
    conn.close()
    gaps.sort(key=lambda x: {"high": 0, "medium": 1}[x["priority"]])
    return gaps


if __name__ == "__main__":
    # Test
    profile = ensure_profile()
    print(f"Profile: {profile['name']}")
    print(f"Pillars: {len(profile.get('content_pillars', []))}")
    
    # Test chat
    response = chat("What should I post about today?")
    print(f"\nPRISM: {response}")