"""
PRISM Database — SQLite local store (mirrors Supabase schema)
Tables: stories, drafts, topics, published, hooks, user_profile, improvements, content_calendar
"""
import sqlite3, json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "database" / "prism.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create all tables. Run once on setup."""
    conn = get_db()
    cur = conn.cursor()
    
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS stories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        source_id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        url TEXT,
        author TEXT,
        points INTEGER DEFAULT 0,
        summary TEXT,
        topics TEXT,
        story_date TEXT,
        fetched_at TEXT DEFAULT CURRENT_TIMESTAMP,
        processed INTEGER DEFAULT 0,
        used_in_content INTEGER DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS drafts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        story_id INTEGER REFERENCES stories(id),
        platform TEXT NOT NULL,
        topic_id TEXT,
        topic_name TEXT,
        format TEXT NOT NULL,
        content TEXT NOT NULL,
        hook TEXT,
        angle TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TEXT
    );
    
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT UNIQUE NOT NULL,
        pillar TEXT NOT NULL,
        description TEXT,
        angles TEXT,
        hook_templates TEXT,
        times_used INTEGER DEFAULT 0,
        times_published INTEGER DEFAULT 0,
        avg_engagement INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1
    );
    
    CREATE TABLE IF NOT EXISTS published (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        draft_id INTEGER REFERENCES drafts(id),
        platform TEXT NOT NULL,
        content TEXT NOT NULL,
        posted_at TEXT,
        story_id INTEGER REFERENCES stories(id),
        impressions INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        saves INTEGER DEFAULT 0,
        replies INTEGER DEFAULT 0,
        reposts INTEGER DEFAULT 0,
        engagement_score INTEGER DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS hooks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hook_type TEXT NOT NULL,
        hook_formula TEXT NOT NULL,
        platform TEXT DEFAULT 'X',
        times_used INTEGER DEFAULT 0,
        times_hit INTEGER DEFAULT 0,
        avg_likes INTEGER DEFAULT 0,
        avg_saves INTEGER DEFAULT 0,
        avg_replies INTEGER DEFAULT 0,
        last_used TEXT
    );
    
    CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        x_handle TEXT,
        bio TEXT,
        focus_areas TEXT,
        content_pillars TEXT,
        voice_style TEXT,
        voice_tone TEXT,
        voice_avoids TEXT,
        platforms TEXT,
        posting_cadence TEXT,
        posting_windows TEXT,
        unique_take TEXT,
        goals TEXT,
        target_audience TEXT,
        follower_count INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS improvements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        change_type TEXT NOT NULL,
        description TEXT NOT NULL,
        impact_score INTEGER DEFAULT 5,
        source TEXT DEFAULT 'manual',
        content_id INTEGER,
        applied INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS content_calendar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        planned_date TEXT NOT NULL,
        pillar TEXT NOT NULL,
        topic TEXT,
        angle TEXT,
        format TEXT DEFAULT 'single',
        status TEXT DEFAULT 'planned',
        draft_id INTEGER REFERENCES drafts(id),
        source TEXT DEFAULT 'auto',
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS seen_stories (
        source TEXT NOT NULL,
        source_id TEXT NOT NULL,
        seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (source, source_id)
    );
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

def story_seen(source, source_id) -> bool:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM seen_stories WHERE source=? AND source_id=?", (source, source_id))
    seen = cur.fetchone() is not None
    conn.close()
    return seen

def mark_story_seen(source, source_id):
    conn = get_db()
    conn.execute("INSERT OR IGNORE INTO seen_stories (source, source_id) VALUES (?, ?)", (source, source_id))
    conn.commit()
    conn.close()

def insert_story(story: dict) -> int:
    """Insert a story if not already seen. Returns story_id or -1 if duplicate."""
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO stories (source, source_id, title, url, author, points, summary, topics, story_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            story['source'], story['source_id'], story['title'], story['url'],
            story.get('author'), story.get('points', 0), story.get('summary'),
            json.dumps(story.get('topics', [])),
            story.get('story_date')
        ))
        conn.commit()
        story_id = cur.lastrowid
        conn.close()
        return story_id
    except sqlite3.IntegrityError:
        conn.close()
        return -1

def get_unprocessed_stories(limit=20):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM stories WHERE processed=0 ORDER BY points DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_story_processed(story_id):
    conn = get_db()
    conn.execute("UPDATE stories SET processed=1 WHERE id=?", (story_id,))
    conn.commit()
    conn.close()

def insert_draft(draft: dict) -> int:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO drafts (story_id, platform, topic_id, topic_name, format, content, hook, angle, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        draft.get('story_id'), draft['platform'], draft.get('topic_id'),
        draft.get('topic_name'), draft['format'], json.dumps(draft['content']),
        draft.get('hook', ''), draft.get('angle', ''), draft.get('status', 'pending')
    ))
    conn.commit()
    draft_id = cur.lastrowid
    conn.close()
    return draft_id

def get_pending_drafts(limit=10):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM drafts WHERE status='pending' ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_draft_status(draft_id, status):
    conn = get_db()
    conn.execute("UPDATE drafts SET status=?, reviewed_at=CURRENT_TIMESTAMP WHERE id=?", (status, draft_id))
    conn.commit()
    conn.close()

def insert_topic(topic: dict):
    conn = get_db()
    conn.execute("""
        INSERT OR IGNORE INTO topics (topic, pillar, description, angles, hook_templates)
        VALUES (?, ?, ?, ?, ?)
    """, (
        topic['topic'], topic['pillar'], topic.get('description'),
        json.dumps(topic.get('angles', [])),
        json.dumps(topic.get('hook_templates', []))
    ))
    conn.commit()
    conn.close()

def get_topics(pillar=None, active=True):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if pillar:
        cur.execute("SELECT * FROM topics WHERE pillar=? AND active=1", (pillar,))
    else:
        cur.execute("SELECT * FROM topics WHERE active=1")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def seed_hooks():
    """Seed the hooks library with proven formulas."""
    conn = get_db()
    hooks = [
        ("I Built X", "I built [specific thing]. Here's what it cost/what I learned/how it works."),
        ("Contrarian", "Everyone thinks [common belief]. They're wrong."),
        ("Counterintuitive", "I expected X. I got Y. Here's why."),
        ("Hard-Won Lesson", "The #1 mistake builders make with [topic]"),
        ("Numbers Breakdown", "[Specific number] [specific outcome]. Here's the real math."),
        ("Nobody Talks About", "Everyone talks about [loud topic]. Here's what matters instead."),
        ("Ship Story", "I shipped [X] in [time]. [Specific outcome]."),
        ("Stop Doing", "Stop doing [X]. Do this instead."),
        ("Prediction", "The future of [X] looks like this."),
        ("Tool Deep Dive", "[Tool] in production: [N] months of real results."),
        ("Cost Analysis", "[$X/month]. [Y] conversations. Real breakdown."),
        ("Market Gap", "The [X] market nobody's building for."),
        ("Framework Compare", "[Framework A] vs [Framework B]: the real answer"),
        ("Architecture", "The architecture nobody's talking about: [X]"),
        ("AI vs Human", "I replaced [human task] with AI. Here's what happened."),
    ]
    for hook_type, formula in hooks:
        conn.execute("""
            INSERT OR IGNORE INTO hooks (hook_type, hook_formula)
            VALUES (?, ?)
        """, (hook_type, formula))
    conn.commit()
    conn.close()

def get_random_hook(limit=5):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM hooks ORDER BY RANDOM() LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ─── User Profile ────────────────────────────────────────────────────────────

def set_user_profile(profile: dict):
    conn = get_db()
    conn.execute("DELETE FROM user_profile")
    conn.execute("""
        INSERT INTO user_profile (
            id, name, x_handle, bio, focus_areas, content_pillars,
            voice_style, voice_tone, voice_avoids, platforms,
            posting_cadence, posting_windows, unique_take,
            goals, target_audience, follower_count, updated_at
        )
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        profile['name'],
        profile.get('x_handle', ''),
        profile.get('bio', ''),
        json.dumps(profile.get('focus_areas', [])),
        json.dumps(profile.get('content_pillars', [])),
        profile.get('voice_style', ''),
        profile.get('voice_tone', ''),
        json.dumps(profile.get('voice_avoids', [])),
        json.dumps(profile.get('platforms', [])),
        profile.get('posting_cadence', ''),
        json.dumps(profile.get('posting_windows', [])),
        profile.get('unique_take', ''),
        profile.get('goals', ''),
        profile.get('target_audience', ''),
        profile.get('follower_count', 0)
    ))
    conn.commit()
    conn.close()

def get_user_profile():
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_profile WHERE id=1")
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    for field in ['focus_areas', 'content_pillars', 'voice_avoids', 'platforms', 'posting_windows']:
        d[field] = json.loads(d[field]) if d.get(field) else []
    return d

# ─── Improvements ────────────────────────────────────────────────────────────

def log_improvement(improvement: dict):
    """Log a content or strategy improvement."""
    conn = get_db()
    conn.execute("""
        INSERT INTO improvements (category, change_type, description, impact_score, source, content_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        improvement['category'],
        improvement['change_type'],
        improvement['description'],
        improvement.get('impact_score', 5),
        improvement.get('source', 'manual'),
        improvement.get('content_id')
    ))
    conn.commit()
    conn.close()

def get_improvements(limit=50):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM improvements ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_improvement_applied(improvement_id):
    conn = get_db()
    conn.execute("UPDATE improvements SET applied=1 WHERE id=?", (improvement_id,))
    conn.commit()
    conn.close()

# ─── Content Calendar ────────────────────────────────────────────────────────

def add_calendar_entry(entry: dict):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO content_calendar (planned_date, pillar, topic, angle, format, status, source, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entry['planned_date'],
        entry['pillar'],
        entry.get('topic', ''),
        entry.get('angle', ''),
        entry.get('format', 'single'),
        entry.get('status', 'planned'),
        entry.get('source', 'auto'),
        entry.get('notes', '')
    ))
    conn.commit()
    entry_id = cur.lastrowid
    conn.close()
    return entry_id

def get_calendar(start_date=None, end_date=None, limit=30):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if start_date:
        cur.execute("""
            SELECT * FROM content_calendar
            WHERE planned_date >= ? AND planned_date <= ?
            ORDER BY planned_date ASC LIMIT ?
        """, (start_date, end_date or start_date, limit))
    else:
        cur.execute("SELECT * FROM content_calendar ORDER BY planned_date ASC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_calendar_status(entry_id, status):
    conn = get_db()
    conn.execute("UPDATE content_calendar SET status=? WHERE id=?", (status, entry_id))
    conn.commit()
    conn.close()

def get_pillar_coverage():
    """Get last-posted date per pillar for gap detection."""
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT pillar, MAX(planned_date) as last_date, COUNT(*) as total
        FROM content_calendar
        WHERE status IN ('planned', 'posted')
        GROUP BY pillar
        ORDER BY last_date ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

if __name__ == "__main__":
    init_db()
    seed_hooks()
    print("✅ PRISM database ready")