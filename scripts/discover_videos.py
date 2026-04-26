#!/usr/bin/env python3
"""
PRISM YouTube Intelligence Pipeline — discover, analyze, score quality videos.
Works with: Playwright (discovery always), yt-dlp + transcript API (evergreen videos only).
Fallback: Use video title + description + chapters for content generation.
"""
import sys, json, subprocess, re, urllib.request, math
from playwright.sync_api import sync_playwright
from youtube_transcript_api import YouTubeTranscriptApi

# ============================================================================
# DISCOVERY: Playwright YouTube Search → video IDs
# ============================================================================

def search_youtube(query, max_results=8):
    """Search YouTube via Playwright, return video IDs + title + view count."""
    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            
            encoded_query = query.replace(" ", "+")
            url = f"https://www.youtube.com/results?search_query={encoded_query}&sp=EgIQAQ%253D%253D"
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            
            video_elements = page.query_selector_all("ytd-video-renderer")
            
            for el in video_elements[:max_results]:
                try:
                    title_el = el.query_selector("#video-title")
                    meta_el = el.query_selector("#meta")
                    if not title_el:
                        continue
                    
                    title = title_el.inner_text().strip()
                    href = title_el.get_attribute("href") or ""
                    
                    vid_match = re.search(r"watch\?v=([a-zA-Z0-9_-]{11})", href)
                    if not vid_match:
                        continue
                    video_id = vid_match.group(1)
                    
                    # Parse meta for view count
                    meta_text = meta_el.inner_text().strip() if meta_el else ""
                    view_count = 0
                    vm = re.search(r"([\d.,]+)\s*(?:Aufrufe|views)", meta_text, re.IGNORECASE)
                    if vm:
                        raw = vm.group(1).replace(",", "").replace(".", "")
                        try:
                            if "Mio" in meta_text or "M" in meta_text:
                                view_count = int(float(raw) * 1_000_000)
                            elif "Tsd" in meta_text or "K" in meta_text:
                                view_count = int(float(raw) * 1_000)
                            else:
                                view_count = int(float(raw))
                        except:
                            pass
                    
                    results.append({
                        "videoId": video_id,
                        "title": title,
                        "url": f"https://youtube.com/watch?v={video_id}",
                        "searchQuery": query,
                        "viewsFromSearch": view_count,
                    })
                except Exception:
                    continue
            
            browser.close()
    except Exception as e:
        print(f"  Playwright search error for '{query}': {e}", file=sys.stderr)
    
    return results

# ============================================================================
# ENRICH: YouTube oEmbed API — title, channel, thumbnail (always works)
# ============================================================================

def get_oembed(video_id):
    """Get title + channel from YouTube oEmbed — reliable, no rate limits."""
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            return {
                "title": data.get("title", ""),
                "channel": data.get("author_name", ""),
                "thumbnail": data.get("thumbnail_url", ""),
            }
    except Exception:
        return {"title": "", "channel": "", "thumbnail": ""}

# ============================================================================
# METADATA: yt-dlp — works for evergreen videos (older than ~1 year)
# ============================================================================

def yt_dlp_metadata(video_id):
    """Get full metadata via yt-dlp — works for older/evergreen videos.
    Returns None if VPS IP is blocked (newer videos)."""
    cmd = [
        "yt-dlp", "--dump-json", "--no-download", "--no-playlist",
        "--socket-timeout", "15",
        f"https://youtube.com/watch?v={video_id}"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if result.returncode == 0:
            return json.loads(result.stdout)
        elif "Sign in to confirm" in result.stderr:
            return None  # IP blocked
    except Exception:
        pass
    return None

# ============================================================================
# TRANSCRIPT: youtube-transcript-api — works for evergreen videos
# ============================================================================

def get_transcript(video_id):
    """Get English transcript via API — works for older videos from non-cloud IPs.
    Returns (transcript_text, error_message)."""
    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=["en"])
        return " ".join(snippet.text for snippet in transcript.snippets), None
    except Exception as e:
        err = str(e)
        return "", err

# ============================================================================
# PLAYWRIGHT WATCH PAGE — description, hashtags, chapters (always works)
# ============================================================================

def get_watch_page(video_id):
    """Extract description + hashtags + chapters from video watch page via Playwright.
    This works even when yt-dlp/transcript API are blocked — it's just page scraping."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"https://www.youtube.com/watch?v={video_id}", timeout=15000)
            page.wait_for_timeout(3500)
            
            data = page.evaluate("""() => {
                // --- Description ---
                var desc = '';
                var de = document.querySelector('#description-inner');
                if (de) desc = de.innerText;

                // --- Upload date ---
                var date = '';
                var da = document.querySelector('#info-text #date');
                if (da) date = da.innerText;

                // --- View count text (raw) ---
                var viewsText = '';
                var vi = document.querySelector('#info-text #count');
                if (vi) viewsText = vi.innerText;

                // --- Parse view count from description (better format) ---
                // Description starts with "4,2 Mio. Aufrufe" or "4.203.862 Aufrufe"
                // Format: digits + separator + label (Mio/Aufrufe)
                var descViewCount = '';
                if (desc) {
                    var dvm = desc.match(/([\d.,]+[\s\xa0]*(?:Mio\.?|Tsd\.?)?[\s\xa0]*(?:Aufrufe|views))/i);
                    if (dvm) descViewCount = dvm[1].trim();
                }

                // --- Channel name ---
                var channel = '';
                var ch = document.querySelector('#channel-name #text a');
                if (ch) channel = ch.innerText;

                // --- Title ---
                var title = '';
                var ti = document.querySelector('h1 yt-formatted-string');
                if (ti) title = ti.innerText;

                // --- Has subtitles button visible ---
                var subBtn = document.querySelector('.ytp-subtitles-button');
                var hasSubs = subBtn !== null;

                // --- Hashtags from description ---
                var hashtags = [];
                if (desc) {
                    var hm = desc.match(/#\\w+/g);
                    if (hm) hashtags = hm.slice(0, 20);
                }

                // --- Chapters (timestamps in description) ---
                var chapters = [];
                if (desc) {
                    var lines = desc.split('\\n');
                    for (var i = 0; i < lines.length; i++) {
                        var ln = lines[i].trim();
                        if (/^\\d{1,2}:\\d{2}(:\\d{2})?\\s/.test(ln)) {
                            chapters.push(ln);
                        }
                    }
                }

                return {
                    description: desc,
                    viewsText: viewsText,
                    descViewCount: descViewCount,
                    uploadDate: date,
                    title: title,
                    channel: channel,
                    hasSubtitles: hasSubs,
                    hashtags: hashtags,
                    chapters: chapters.slice(0, 20)
                };
            }""")
            
            browser.close()
            return data
    except Exception as e:
        return {"description": "", "viewsText": "", "viewCount": 0, "uploadDate": "",
                "title": "", "channel": "", "hasSubtitles": False,
                "hashtags": [], "chapters": []}

# ============================================================================
# VIEW COUNT PARSER — handle German/English formats from description
# ============================================================================

def parse_view_count(views_text, fallback=0):
    """Parse view count from text like '4.203.789 Aufrufe' or '4,2 Mio. Aufrufe' or '526.170 Aufrufe'."""
    if not views_text:
        return fallback
    text = views_text.replace("\n", " ").strip()
    # Remove labels
    text_clean = text.replace("Aufrufe", "").replace("views", "").replace("Mio.", "M").replace("Mio", "M").replace("Tsd.", "K").replace("Tsd", "K").strip()
    
    multiplier = 1
    # Detect multiplier from the cleaned text
    # "4,2M" or "4,2 M" → million, "20,4K" or "20,4 K" → thousand
    # Check last word for M/K OR look for M/K anywhere as standalone suffix
    text_last = text_clean.split()[-1] if text_clean.split() else ""
    if "M" in text_clean.split()[-1] if text_clean.split() else False:
        multiplier = 1_000_000
    elif "K" in text_clean.split()[-1] if text_clean.split() else False:
        multiplier = 1_000
    
    # Extract ALL digit sequences from the text
    digit_seqs = re.findall(r"\d+", text_clean)
    if not digit_seqs:
        return fallback

    if multiplier == 1_000_000 or multiplier == 1_000:
        # Decimal formats: "4,2M" (comma) or "46.0M" (dot)
        if len(digit_seqs) == 2:
            if "," in text_clean:
                # "4,2M" → 4.2 * multiplier
                try:
                    return int(float(digit_seqs[0] + "." + digit_seqs[1]) * multiplier)
                except:
                    pass
            elif "." in text_clean and ("M" in text_clean or "K" in text_clean):
                # "46.0M" → 46.0 * multiplier
                try:
                    return int(float(digit_seqs[0] + "." + digit_seqs[1]) * multiplier)
                except:
                    pass
        # Fallback: join all digits
        raw = "".join(digit_seqs)
        try:
            return int(raw) * multiplier
        except:
            pass
    else:
        # No multiplier — European thousands: "20.421" → digit_seqs=['20','421'] → "20421"
        # or plain number: digit_seqs=['204328'] → "204328"
        raw = "".join(digit_seqs)
        try:
            return int(raw)
        except:
            pass

    return fallback

# ============================================================================
# SCORING
# ============================================================================

def score_video(views, likes, duration, has_subtitles, has_transcript, word_count):
    """Score a video by quality signals. Higher = better for content extraction."""
    score = 0
    
    # View count tier
    if views > 5_000_000: score += 35
    elif views > 1_000_000: score += 28
    elif views > 500_000: score += 22
    elif views > 100_000: score += 16
    elif views > 10_000: score += 10
    elif views > 0: score += 5
    
    # Like/view ratio bonus
    if views > 0 and likes > 0:
        ratio = likes / views
        if ratio > 0.05: score += 25
        elif ratio > 0.03: score += 18
        elif ratio > 0.015: score += 12
        elif ratio > 0.005: score += 7
    
    # Duration: prefer 5-30 min (substantial, good for content)
    if 300 <= duration <= 1800: score += 18
    elif 180 <= duration < 300: score += 10
    elif 60 <= duration < 180: score += 5
    elif duration > 3600: score -= 5  # penalize extremely long
    elif duration == 0: score -= 3   # unknown duration slightly penalized
    
    # Content availability
    if has_subtitles: score += 5
    if has_transcript and word_count > 1000: score += 20
    elif has_transcript: score += 10
    
    # Content richness bonus (description + chapters = rich content)
    if word_count > 5000: score += 10
    elif word_count > 1000: score += 5
    
    return score

# ============================================================================
# FULL VIDEO ANALYSIS
# ============================================================================

def analyze_video(video_id, search_info=None):
    """
    Full analysis of a single video.
    
    Sources tried (in order):
      1. yt-dlp — full metadata (views, likes, duration, transcript)
         → works for evergreen videos from non-cloud IPs
      2. Playwright watch page — description, hashtags, chapters, view count
         → ALWAYS works (scrapes rendered page)
      3. oEmbed — title, channel, thumbnail
         → ALWAYS works (public API)
      4. YouTube transcript API — full transcript
         → works for evergreen videos from non-cloud IPs
    """
    oembed = get_oembed(video_id)
    yt_meta = yt_dlp_metadata(video_id)
    watch = get_watch_page(video_id)
    
    # ---- Determine source and extract metadata ----
    if yt_meta and yt_meta.get("view_count"):
        # yt-dlp succeeded — use its rich data
        title = yt_meta.get("title") or oembed.get("title", "")
        channel = yt_meta.get("channel") or oembed.get("channel", "")
        views = yt_meta.get("view_count") or 0
        likes = yt_meta.get("like_count") or 0
        duration = yt_meta.get("duration") or 0
        duration_str = yt_meta.get("duration_string") or fmt_duration(duration)
        upload_date = yt_meta.get("upload_date") or ""
        upload_date_str = fmt_date(upload_date)
        has_subs = bool(yt_meta.get("subtitles") or yt_meta.get("automatic_captions"))
        description = (yt_meta.get("description") or "")[:1000]
        hashtags = list(set(re.findall(r"#\w+", description)))[:15]
        chapters = extract_chapters(description)
        source = "yt-dlp"
        word_count = 0
        transcript = ""
        trans_err = None
        
        # Try transcript API only if yt-dlp worked (same IP constraint)
        transcript, trans_err = get_transcript(video_id)
        if transcript:
            word_count = len(transcript.split())
    
    else:
        # yt-dlp blocked — use Playwright watch page + oEmbed
        title = watch.get("title") or oembed.get("title", "") or (search_info.get("title") if search_info else "")
        channel = watch.get("channel") or oembed.get("channel", "")
        
        # Views: parse from description (cleanest format), then search results
        views_desc = parse_view_count(watch.get("descViewCount", ""), 0)
        views_search = search_info.get("viewsFromSearch", 0) if search_info else 0
        if views_desc > 0:
            views = views_desc
        elif views_search > 0:
            views = views_search
        else:
            views = parse_view_count(watch.get("viewsText", ""))
        
        likes = 0
        duration = 0  # Can't get duration without yt-dlp or player JS
        duration_str = ""
        upload_date_str = watch.get("uploadDate", "")
        has_subs = watch.get("hasSubtitles", False)
        description = watch.get("description", "")[:1000]
        hashtags = watch.get("hashtags", [])[:15]
        chapters = watch.get("chapters", [])[:15]
        source = "watch-page"
        transcript = ""
        trans_err = "Transcript unavailable — VPS IP is blocked by YouTube for newer videos. Use evergreen videos (1+ year old) or run from a residential IP."
        word_count = len(description.split())
    
    quality_score = score_video(views, likes, duration, has_subs, bool(transcript), word_count)
    read_time = round(word_count / 200, 1) if word_count else 0
    
    return {
        "videoId": video_id,
        "title": title,
        "channel": channel,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "thumbnail": oembed.get("thumbnail", f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"),
        "topic": search_info.get("topic", "") if search_info else "",
        "viewCount": views,
        "viewCountFormatted": fmt_number(views),
        "likeCount": likes,
        "likeCountFormatted": fmt_number(likes),
        "duration": duration,
        "durationString": duration_str,
        "uploadDate": upload_date_str,
        "qualityScore": quality_score,
        "hasSubtitles": has_subs,
        "hasTranscript": bool(transcript),
        "description": description,
        "transcript": transcript[:3000] if transcript else "",
        "transcriptError": trans_err,
        "wordCount": word_count,
        "readTimeMinutes": read_time,
        "hashtags": hashtags[:10],
        "chapters": chapters[:15],
        "source": source,
        # VPS limitation note
        "limitation": "VPS IP is blocked by YouTube for metadata/transcripts of newer videos. Evergreen videos (1+ year old) work fine. Use YouTube Data API v3 for universal access." if source == "watch-page" and not transcript else "",
    }

def fmt_duration(seconds):
    if not seconds or (isinstance(seconds, float) and math.isnan(seconds)):
        return ""
    try:
        seconds = int(seconds)
    except (ValueError, TypeError):
        return ""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0: return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

def fmt_date(date_str):
    if not date_str or len(date_str) != 8: return date_str
    try:
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    except: return date_str

def fmt_number(n):
    if n is None or n == 0: return "0"
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.1f}K"
    return str(n)

def extract_chapters(description):
    if not description: return []
    chapters = []
    for line in description.split("\n"):
        line = line.strip()
        if re.match(r"^\d{1,2}:\d{2}(:\d{2})?\s", line):
            chapters.append(line)
    return chapters[:15]

# ============================================================================
# DISCOVER VIDEOS ACROSS TOPICS
# ============================================================================

def discover_videos(topics, per_topic=4):
    """Discover videos across multiple topics via Playwright."""
    all_videos = []
    seen = set()
    
    for topic in topics:
        queries = [topic]
        for q in queries:
            try:
                results = search_youtube(q, max_results=per_topic)
                for v in results:
                    if v["videoId"] not in seen:
                        seen.add(v["videoId"])
                        all_videos.append({**v, "topic": topic})
            except Exception as e:
                print(f"  Error on '{q}': {e}", file=sys.stderr)
    
    return all_videos

# ============================================================================
# FULL PIPELINE
# ============================================================================

def full_scan(topics=None, per_topic=4, max_total=20):
    """
    Complete PRISM YouTube intelligence pipeline.
    discover → enrich → analyze → score → rank
    
    Args:
        topics: list of search topics
        per_topic: videos per topic
        max_total: max total videos to analyze
    
    Returns:
        List of video analysis dicts, sorted by quality score (highest first)
    """
    if topics is None:
        topics = ["AI agents automation", "content creation strategy", "social media growth"]
    
    print(f"PRISM YouTube Scan: {topics}", file=sys.stderr)
    
    # Step 1: Discover
    discovered = discover_videos(topics, per_topic=per_topic)
    print(f"  Discovered {len(discovered)} candidates", file=sys.stderr)
    
    # Step 2: Dedupe
    seen_ids = set()
    unique = []
    for v in discovered:
        if v["videoId"] not in seen_ids:
            seen_ids.add(v["videoId"])
            unique.append(v)
    
    # Step 3: Analyze
    results = []
    for v in unique[:max_total]:
        vid = v["videoId"]
        print(f"  Analyzing: {vid} — {v.get('title', '')[:40]}", file=sys.stderr)
        try:
            analysis = analyze_video(vid, search_info=v)
            results.append(analysis)
            
            pts = analysis["qualityScore"]
            src = analysis["source"]
            dur = analysis["durationString"] or "?"
            views = analysis["viewCountFormatted"]
            words = analysis["wordCount"]
            has_t = analysis["hasTranscript"]
            print(f"    [{pts:2d}pts][{src}] {dur:>8} | {views:>8} views | {words:5d} desc_words | transcript={has_t}", file=sys.stderr)
        except Exception as e:
            print(f"    ERROR: {e}", file=sys.stderr)
    
    # Step 4: Rank
    results.sort(key=lambda x: x["qualityScore"], reverse=True)
    return results

if __name__ == "__main__":
    topics = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    results = full_scan(topics)
    
    print("\n" + "="*70)
    print(f"TOP {len(results)} QUALITY VIDEOS FOR CONTENT:")
    print("="*70)
    for i, r in enumerate(results, 1):
        print(f"\n{i}. [{r['qualityScore']:2d}pts] {r.get('title','?')[:65]}")
        print(f"   {r.get('channel','?')} | {r.get('durationString','?')} | {r.get('viewCountFormatted','?')} views | {r.get('readTimeMinutes','?')} min")
        print(f"   Transcript: {'YES' if r.get('hasTranscript') else 'NO (desc only)'}")
        if r.get('chapters'):
            chaps = ", ".join(r["chapters"][:3])
            print(f"   Chapters: {chaps}")
        if r.get('hashtags'):
            print(f"   {', '.join(r['hashtags'][:5])}")
        print(f"   {r.get('url','')}")
        if r.get('limitation'):
            print(f"   NOTE: {r['limitation']}")
    
    print("\n--- JSON OUTPUT ---")
    print(json.dumps(results, indent=2, ensure_ascii=False))
