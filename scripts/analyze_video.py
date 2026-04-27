#!/usr/bin/env python3
"""Analyze a YouTube video — metadata + transcript."""
import sys, json, urllib.request, urllib.parse
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled, VideoUnavailable, 
    TooManyRequests, CouldNotLatestRetrieve
)

def get_transcript(video_id):
    """Fetch transcript — auto-generated or manual."""
    errors = {}
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        return "".join(t["text"] + " " for t in transcript).strip(), None
    except Exception as e:
        errors[type(e).__name__] = str(e)
    
    # Try any available language
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        for t in transcript_list:
            try:
                trans = t.fetch()
                text = "".join(entry["text"] + " " for entry in trans).strip()
                return text, t.language_code
            except:
                continue
    except Exception as e:
        errors["list_error"] = str(e)
    
    return "", errors

def analyze_video(video_id):
    """Full analysis — metadata from Invidious + transcript."""
    # Get transcript first (most important)
    transcript, trans_error = get_transcript(video_id)
    
    # Get metadata from Invidious
    metadata = {}
    for instance in ["yewtu.be", "vid.puffyan.us", "invidious.privacyredirect.com"]:
        try:
            url = f"https://{instance}/api/v1/videos/{video_id}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read())
                metadata = {
                    "title": data.get("title",""),
                    "author": data.get("author",""),
                    "views": data.get("viewCount", 0),
                    "likes": data.get("likeCount", 0),
                    "lengthSeconds": data.get("lengthSeconds", 0),
                    "published": data.get("published", 0),
                    "description": data.get("description",""),
                    "tags": data.get("keywords", []),
                }
                break
        except:
            continue
    
    word_count = len(transcript.split()) if transcript else 0
    read_time_minutes = word_count / 200 if word_count else 0
    
    return {
        "videoId": video_id,
        "transcript": transcript,
        "transcriptError": trans_error,
        "wordCount": word_count,
        "readTimeMinutes": round(read_time_minutes, 1),
        **metadata
    }

if __name__ == "__main__":
    video_id = sys.argv[1]
    result = analyze_video(video_id)
    print(json.dumps(result, indent=2, ensure_ascii=False))
