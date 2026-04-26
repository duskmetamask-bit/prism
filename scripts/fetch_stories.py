"""
PRISM Research Engine
Fetches stories from: Hacker News, GitHub Trending, AI newsletters
Stores to SQLite, avoids duplicates
"""
import requests, json, re
from datetime import datetime, timedelta
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from database.prism_db import insert_story, story_seen, mark_story_seen

HN_ALGOLIA = "https://hn.algolia.com/api/v1/search"

# ─── Hacker News via Algolia ───────────────────────────────────────────────

def fetch_hackernews(query="AI agent", days_back=7, limit=30):
    """
    Fetch AI-related stories from HN via Algolia API.
    Returns list of story dicts.
    """
    from_ts = int((datetime.now() - timedelta(days=days_back)).timestamp())
    
    url = f"{HN_ALGOLIA}"
    params = {
        "query": query,
        "tags": "story",
        "numericFilters": f"created_at_i>{from_ts}",
        "hitsPerPage": limit,
        "attributesToRetrieve": "title,url,author,points,created_at,objectID,story_text",
    }
    
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"❌ HN fetch failed: {e}")
        return []
    
    stories = []
    for hit in data.get("hits", []):
        source_id = hit.get("objectID", "")
        title = hit.get("title", "")
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={source_id}"
        author = hit.get("author", "")
        points = hit.get("points", 0)
        created = hit.get("created_at", "")[:10]
        
        # Dedupe
        if story_seen("hackernews", source_id):
            continue
        
        mark_story_seen("hackernews", source_id)
        
        stories.append({
            "source": "hackernews",
            "source_id": source_id,
            "title": title,
            "url": url,
            "author": author,
            "points": points,
            "summary": hit.get("story_text", "")[:500] if hit.get("story_text") else "",
            "topics": _extract_topics(title + " " + (hit.get("story_text") or "")),
            "story_date": created,
        })
    
    print(f"📰 HN: fetched {len(stories)} new stories")
    return stories


# ─── GitHub Trending ───────────────────────────────────────────────────────

def fetch_github_trending(lang="python", days_back=30):
    """
    Fetch trending GitHub repos for a language using GitHub Search API.
    """
    try:
        query = f"ai agent created:>{days_back}"
        r = requests.get(
            f"https://api.github.com/search/repositories",
            params={"q": query, "sort": "stars", "order": "desc", "per_page": 15},
            timeout=20,
            headers={"Accept": "application/vnd.github.v3+json"}
        )
        r.raise_for_status()
        data = r.json()
        repos = data.get("items", [])
    except Exception as e:
        print(f"❌ GitHub trending fetch failed: {e}")
        return []
    
    stories = []
    for repo in repos[:10]:  # top 10
        source_id = f"github_{repo.get('full_name', '')}"
        
        if story_seen("github", source_id):
            continue
        mark_story_seen("github", source_id)
        
        stories.append({
            "source": "github",
            "source_id": source_id,
            "title": f"[GitHub] {repo.get('full_name', '')} — {repo.get('description', '')}",
            "url": f"https://github.com/{repo.get('full_name', '')}",
            "author": repo.get('owner', {}).get('login', ''),
            "points": repo.get('stargazers_count', 0),
            "summary": repo.get('description', ''),
            "topics": [lang, "open source", "trending"],
            "story_date": repo.get('created_at', '')[:10] if repo.get('created_at') else datetime.now().strftime("%Y-%m-%d"),
        })
    
    print(f"🐙 GitHub trending: fetched {len(stories)} new repos")
    return stories


# ─── RSS Feeds ────────────────────────────────────────────────────────────

RSS_FEEDS = {
    "venturebeat": "https://venturebeat.com/category/ai/feed/",
    "techcrunch_ai": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "mit_tech_review": "https://www.technologyreview.com/feed/",
}

def fetch_rss(feed_name, feed_url):
    """Fetch and parse RSS feed."""
    try:
        r = requests.get(feed_url, timeout=15, headers={"User-Agent": "PRISM/1.0"})
        r.raise_for_status()
        import feedparser
        feed = feedparser.parse(r.text)
    except ImportError:
        print("⚠️ feedparser not installed, skipping RSS")
        return []
    except Exception as e:
        print(f"❌ RSS fetch failed for {feed_name}: {e}")
        return []
    
    stories = []
    for entry in feed.entries[:10]:
        source_id = f"{feed_name}_{hash(entry.get('link', ''))}"
        
        if story_seen(feed_name, source_id):
            continue
        mark_story_seen(feed_name, source_id)
        
        summary = ""
        if hasattr(entry, 'summary'):
            summary = re.sub('<[^<]+?>', '', entry.summary)[:500]
        elif hasattr(entry, 'description'):
            summary = re.sub('<[^<]+?>', '', entry.description)[:500]
        
        stories.append({
            "source": feed_name,
            "source_id": source_id,
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "author": entry.get("author", ""),
            "points": 0,
            "summary": summary,
            "topics": _extract_topics(entry.get("title", "") + " " + summary),
            "story_date": entry.get("published", "")[:10] if hasattr(entry, "published") else "",
        })
    
    print(f"📡 RSS ({feed_name}): fetched {len(stories)} new items")
    return stories


# ─── Topic Extraction ────────────────────────────────────────────────────

TOPIC_KEYWORDS = {
    "voice_ai": ["voice AI", "speech", "VAPI", "elevenlabs", "realtime", "phone", "call"],
    "content_ai": ["content", "writing", "SEO", "blog", "newsletter", "social media"],
    "ai_agents": ["agent", "multi-agent", "fleet", "orchestrat", "autonomous"],
    "llm": ["GPT", "Claude", "Gemini", "LLM", "model", "OpenAI", "Anthropic"],
    "infrastructure": ["vector", "database", "webhook", "API", "deploy", "Vercel", "Supabase"],
    "business_ai": ["SaaS", "startup", "pricing", "ROI", "cost", "efficiency"],
    "open_source": ["open source", "github", "langchain", "llamaindex", "crewai"],
}

def _extract_topics(text: str) -> list:
    text_lower = text.lower()
    found = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw.lower() in text_lower for kw in keywords):
            found.append(topic)
    return found if found else ["general"]


# ─── Main fetch ───────────────────────────────────────────────────────────

def fetch_all_sources():
    """Fetch from all sources, store new stories, return count."""
    all_stories = []
    
    # HN - multiple queries to cover different angles
    for query in ["AI agent", "voice AI", "content AI automation", "LLM infrastructure", "multi-agent systems"]:
        stories = fetch_hackernews(query=query, days_back=7, limit=20)
        all_stories.extend(stories)
    
    # GitHub trending - AI agent repos
    stories = fetch_github_trending()
    all_stories.extend(stories)
    
    # RSS
    for name, url in RSS_FEEDS.items():
        stories = fetch_rss(name, url)
        all_stories.extend(stories)
    
    # Store to DB
    stored = 0
    for story in all_stories:
        sid = insert_story(story)
        if sid > 0:
            stored += 1
    
    print(f"✅ fetch_all: {stored} new stories stored")
    return stored


if __name__ == "__main__":
    count = fetch_all_sources()
    print(f"\n📊 Total new stories fetched: {count}")
