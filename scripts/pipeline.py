#!/usr/bin/env python3
"""PRISM YouTube Intelligence Pipeline — discover quality videos, analyze, transform."""
import sys, json, os, re
sys.path.insert(0, os.path.dirname(__file__))

from discover_videos import search_invidious
from analyze_video import analyze_video

def score_video(video):
    """Score a video by quality signals."""
    views = video.get("views", 0) or 0
    likes = video.get("likes", 0) or 0
    length = video.get("lengthSeconds", 0) or 0
    desc = video.get("description", "") or ""
    
    score = 0
    
    # Views — prefer established but not massive (less saturated)
    if views > 10000: score += 30
    elif views > 1000: score += 20
    elif views > 100: score += 10
    
    # Like ratio — quality indicator
    if views > 0 and likes > 0:
        ratio = likes / views
        if ratio > 0.05: score += 25
        elif ratio > 0.03: score += 15
        elif ratio > 0.01: score += 10
    
    # Length — prefer 5-30 min (good for content extraction)
    if 300 <= length <= 1800: score += 15
    elif 180 < length < 300: score += 8  # short form okay
    
    # Has description (indicates effort)
    if len(desc) > 200: score += 10
    
    return score

def discover_and_analyze_topics(topics, videos_per_topic=5):
    """Main pipeline — discover videos across topics, score and rank."""
    all_videos = []
    
    for topic in topics:
        # Search with quality modifiers
        queries = [topic, f"{topic} tutorial", f"{topic} explained"]
        for q in queries:
            try:
                results = search_invidious(q, limit=videos_per_topic)
                all_videos.extend(results)
            except Exception as e:
                print(f"Search error for {q}: {e}", file=sys.stderr)
    
    # Dedupe by videoId
    seen = set()
    unique = []
    for v in all_videos:
        if v["videoId"] not in seen:
            seen.add(v["videoId"])
            unique.append(v)
    
    # Score and sort
    for v in unique:
        v["qualityScore"] = score_video(v)
    unique.sort(key=lambda x: x["qualityScore"], reverse=True)
    
    return unique[:20]  # Top 20 across all topics

def full_pipeline(topics=None, output="json"):
    """Run full pipeline: discover → analyze → format."""
    if topics is None:
        topics = ["AI agents", "automation", "content creation", "social media growth"]
    
    print(f"Discovering videos for: {topics}", file=sys.stderr)
    videos = discover_and_analyze_topics(topics)
    print(f"Found {len(videos)} quality videos", file=sys.stderr)
    
    analyzed = []
    for v in videos:
        vid = analyze_video(v["videoId"])
        vid["discoveryQuery"] = v.get("discoveryQuery", "")
        vid["qualityScore"] = v.get("qualityScore", 0)
        analyzed.append(vid)
    
    return analyzed

if __name__ == "__main__":
    topics = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    results = full_pipeline(topics)
    print(json.dumps(results, indent=2, ensure_ascii=False))
