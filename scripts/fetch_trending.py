"""
PRISM Trend Intelligence — Daily X/Twitter Trend Scraper
Fetches trending topics, hot posts, and trending hashtags WITHOUT X API.
Uses web scraping + search to gather what's hot in AI/builder space.
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("[!] Missing dependencies. Run: pip3 install requests beautifulsoup4 lxml")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from database.prism_db import get_db


# ─── Config ──────────────────────────────────────────────────────────────────

SEARCH_TERMS = [
    "AI agents 2026",
    "builder tools AI",
    "no-code automation",
    "AI productivity",
    "Claude AI agents",
    "OpenAI agents",
    "local AI models",
    "hermes AI agents",
    "automation agency",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ─── Trending Sources ─────────────────────────────────────────────────────────

def scrape_twitter_search_results(query, limit=10):
    """Scrape latest tweets for a search term via Nitter (no auth)."""
    results = []
    try:
        nitter_instances = [
            "nitter.poast.org",
            "nitter.privacydev.net",
            "nitter.fly.dev",
            "xcancel.com",
        ]
        
        for instance in nitter_instances:
            try:
                url = f"https://{instance}/search?q={requests.utils.quote(query)}&f=tweets"
                resp = requests.get(url, headers=HEADERS, timeout=8)
                if resp.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(resp.text, "lxml")
                tweets = soup.select("div.timeline-item")
                
                for tweet in tweets[:limit]:
                    try:
                        content_elem = tweet.select_one("div.tweet-content")
                        content = content_elem.get_text(strip=True) if content_elem else ""
                        
                        link_elem = tweet.select_one("a[href*='twitter.com']")
                        link = link_elem["href"] if link_elem else ""
                        
                        if content and len(content) > 20:
                            results.append({
                                "query": query,
                                "content": content[:500],
                                "url": link,
                                "likes": 0, "retweets": 0, "replies": 0,
                                "engagement": 0,
                                "scraped_at": datetime.now().isoformat(),
                            })
                    except Exception:
                        continue
                        
                if results:
                    print(f"  ✅ {instance} — {len(results)} tweets for '{query}'")
                    break
            except Exception:
                continue
                
    except Exception as e:
        print(f"  ⚠️ Twitter search error for '{query}': {e}")
    
    return results


def scrape_google_trends(query, limit=10):
    """Scrape Google Trends / News for a query."""
    results = []
    try:
        url = f"https://www.google.com/search?q={requests.utils.quote(query + ' 2026 AI')}&tbm=nws"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "lxml")
            articles = soup.select("div.SoaBEf")[:limit]
            for article in articles:
                try:
                    title = ""
                    snippet = ""
                    title_elem = article.select_one("div.MBeuO")
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                    snippet_elem = article.select_one("div.GI74Re")
                    if snippet_elem:
                        snippet = snippet_elem.get_text(strip=True)
                    if title:
                        results.append({
                            "query": query,
                            "title": title[:200],
                            "snippet": snippet[:300],
                            "source": "google_news",
                            "scraped_at": datetime.now().isoformat(),
                        })
                except Exception:
                    continue
    except Exception as e:
        print(f"  ⚠️ Google News error: {e}")
    return results


def scrape_tech_news():
    """Scrape what's hot in AI/tech news."""
    results = []
    sources = [
        ("Hacker News", "https://news.ycombinator.com/"),
        ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/"),
    ]
    
    for name, url in sources:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "lxml")
            
            if "Hacker News" in name:
                items = soup.select("tr.athing")[:15]
                for item in items:
                    try:
                        title_elem = item.select_one("span.titleline > a")
                        title = title_elem.get_text(strip=True) if title_elem else ""
                        score_elem = item.select_one("span.score")
                        score = int(score_elem.get_text().split()[0]) if score_elem else 0
                        link = title_elem["href"] if title_elem and title_elem.has_attr("href") else ""
                        
                        if title and score > 10:
                            results.append({
                                "source": "hacker_news",
                                "title": title[:200],
                                "url": link,
                                "points": score,
                                "scraped_at": datetime.now().isoformat(),
                            })
                    except Exception:
                        continue
            else:
                articles = soup.select("article")[:10]
                for article in articles:
                    try:
                        title_elem = article.select_one("h2, h3")
                        title = title_elem.get_text(strip=True) if title_elem else ""
                        link_elem = article.select_one("a[href]")
                        link = link_elem["href"] if link_elem else ""
                        
                        if title and len(title) > 10:
                            results.append({
                                "source": name.lower().replace(" ", "_"),
                                "title": title[:200],
                                "url": link,
                                "scraped_at": datetime.now().isoformat(),
                            })
                    except Exception:
                        continue
            
            print(f"  ✅ {name} — {len(results)} items")
        except Exception as e:
            print(f"  ⚠️ {name} error: {e}")
    
    return results


def scrape_hashtags():
    """Discover trending hashtags in AI/builder space."""
    hashtags = []
    try:
        url = "https://xcancel.com/search?q=%23AI+%23builders&f=tweets"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "lxml")
            tags = soup.select("a[href*='/tag/']")
            found = set()
            for tag in tags:
                hashtag = tag.get_text(strip=True)
                if hashtag.startswith("#") and hashtag not in found:
                    found.add(hashtag)
                    hashtags.append({
                        "hashtag": hashtag,
                        "scraped_at": datetime.now().isoformat(),
                    })
        print(f"  ✅ Hashtags — found {len(hashtags)}")
    except Exception as e:
        print(f"  ⚠️ Hashtag scrape error: {e}")
    
    return hashtags[:20]


# ─── Database ─────────────────────────────────────────────────────────────────

def save_trending_results(tweets, news, tech_news, hashtags):
    """Save all scraped data to PRISM database."""
    import sqlite3
    from database.prism_db import get_db
    conn = get_db()
    cur = conn.cursor()
    saved = 0
    
    for tweet in tweets:
        try:
            cur.execute("""
                INSERT OR IGNORE INTO trending_tweets 
                (query, content, url, likes, retweets, replies, engagement, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tweet["query"], tweet["content"], tweet.get("url", ""),
                tweet["likes"], tweet["retweets"], tweet["replies"],
                tweet["engagement"], tweet["scraped_at"]
            ))
            if cur.rowcount > 0:
                saved += 1
        except Exception as e:
            pass
    
    for item in news:
        try:
            cur.execute("""
                INSERT OR IGNORE INTO trending_news 
                (query, title, snippet, source, scraped_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                item.get("query", ""), item.get("title", ""),
                item.get("snippet", ""), item.get("source", "web"),
                item["scraped_at"]
            ))
            if cur.rowcount > 0:
                saved += 1
        except Exception:
            pass
    
    for item in tech_news:
        try:
            cur.execute("""
                INSERT OR IGNORE INTO trending_news 
                (title, url, source, points, scraped_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                item["title"], item.get("url", ""),
                item["source"], item.get("points", 0),
                item["scraped_at"]
            ))
            if cur.rowcount > 0:
                saved += 1
        except Exception:
            pass
    
    for tag in hashtags:
        try:
            cur.execute("""
                INSERT OR IGNORE INTO trending_hashtags (hashtag, scraped_at)
                VALUES (?, ?)
            """, (tag["hashtag"], tag["scraped_at"]))
            if cur.rowcount > 0:
                saved += 1
        except Exception:
            pass
    
    conn.commit()
    conn.close()
    return saved


def ensure_trending_tables():
    """Create trending tables if they don't exist."""
    import sqlite3
    from database.prism_db import get_db
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS trending_tweets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            content TEXT NOT NULL,
            url TEXT,
            likes INTEGER DEFAULT 0,
            retweets INTEGER DEFAULT 0,
            replies INTEGER DEFAULT 0,
            engagement INTEGER DEFAULT 0,
            scraped_at TEXT NOT NULL,
            UNIQUE(content)
        );
        
        CREATE TABLE IF NOT EXISTS trending_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            title TEXT NOT NULL,
            snippet TEXT,
            source TEXT DEFAULT 'web',
            points INTEGER DEFAULT 0,
            scraped_at TEXT NOT NULL,
            UNIQUE(title)
        );
        
        CREATE TABLE IF NOT EXISTS trending_hashtags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hashtag TEXT UNIQUE NOT NULL,
            scraped_at TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS trend_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_date TEXT NOT NULL UNIQUE,
            tweets_scraped INTEGER DEFAULT 0,
            news_scraped INTEGER DEFAULT 0,
            hashtags_scraped INTEGER DEFAULT 0,
            top_topic TEXT,
            top_topic_engagement INTEGER DEFAULT 0,
            generated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print("  ✅ Trending tables ready")


def get_top_trending(limit=5):
    """Get top trending topics from today's scrape."""
    import sqlite3
    from database.prism_db import get_db
    conn = get_db()
    conn.row_factory = sqlite3.Row
    
    cur = conn.cursor()
    cur.execute("""
        SELECT content, engagement, likes, scraped_at 
        FROM trending_tweets 
        ORDER BY engagement DESC LIMIT ?
    """, (limit,))
    top_tweets = [dict(r) for r in cur.fetchall()]
    
    cur.execute("""
        SELECT title, snippet, source, points 
        FROM trending_news 
        ORDER BY scraped_at DESC LIMIT ?
    """, (limit,))
    top_news = [dict(r) for r in cur.fetchall()]
    
    cur.execute("SELECT hashtag FROM trending_hashtags LIMIT ?", (limit,))
    top_hashtags = [r["hashtag"] for r in cur.fetchall()]
    
    conn.close()
    return {
        "top_tweets": top_tweets,
        "top_news": top_news,
        "top_hashtags": top_hashtags,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    """Run full trend intelligence scrape."""
    import sqlite3
    print("[*] PRISM Trend Intelligence — Daily Scrape")
    print(f"[*] Started: {datetime.now().isoformat()}")
    
    ensure_trending_tables()
    
    print("\n[*] Scraping X/Twitter search results...")
    all_tweets = []
    for term in SEARCH_TERMS:
        tweets = scrape_twitter_search_results(term, limit=10)
        all_tweets.extend(tweets)
    print(f"  → Total tweets: {len(all_tweets)}")
    
    print("\n[*] Scraping Google News trends...")
    all_news = []
    for term in SEARCH_TERMS[:5]:
        news = scrape_google_trends(term, limit=5)
        all_news.extend(news)
    print(f"  → Total news: {len(all_news)}")
    
    print("\n[*] Scraping Tech News sources...")
    tech_news = scrape_tech_news()
    
    print("\n[*] Discovering trending hashtags...")
    hashtags = scrape_hashtags()
    
    print("\n[*] Saving to PRISM database...")
    saved = save_trending_results(all_tweets, all_news, tech_news, hashtags)
    print(f"  ✅ Saved {saved} items")
    
    print(f"\n[*] Scrape complete!")
    print(f"    Tweets: {len(all_tweets)}")
    print(f"    News: {len(all_news) + len(tech_news)}")
    print(f"    Hashtags: {len(hashtags)}")
    
    top = get_top_trending(limit=3)
    if top["top_tweets"]:
        print(f"\n🔥 Top tweet: {top['top_tweets'][0]['content'][:100]}...")
    if top["top_news"]:
        print(f"📰 Top news: {top['top_news'][0]['title'][:80]}")
    if top["top_hashtags"]:
        print(f"#️⃣  Hashtags: {', '.join(top['top_hashtags'][:5])}")
    
    return {"tweets": len(all_tweets), "news": len(all_news) + len(tech_news), "hashtags": len(hashtags), "saved": saved}


if __name__ == "__main__":
    result = main()
    sys.exit(0)
