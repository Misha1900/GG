#!/usr/bin/env python3
"""
YouTube niche/keyword search via the official YouTube Data API v3.

Free, official, no scraping — uses YOUTUBE_API_KEY against googleapis.com.
Returns videos with real stats (views, likes, comments, duration) and each
video's channel subscriber count, so outliers (views far above what the
channel's size would predict) are visible directly in the output.

Usage:
    python yt_niche_search.py "QUERY" [--limit 25] [--order relevance|viewCount|date|rating]
                                       [--published-after YYYY-MM-DD] [--region RU] [--lang ru]

Requires: pip install requests ; export YOUTUBE_API_KEY=...
"""

import argparse
import os
import sys
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("ERROR: the 'requests' package is required. Install with: pip install requests")
    sys.exit(1)

API_BASE = "https://www.googleapis.com/youtube/v3"


def human_number(n):
    if n is None:
        return "N/A"
    n = int(n)
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def parse_iso8601_duration(duration):
    """Parse ISO 8601 duration (PT#H#M#S) into seconds."""
    import re
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration or "")
    if not m:
        return None
    h, mnt, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mnt * 60 + s


def format_duration(seconds):
    if seconds is None:
        return "Unknown"
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def api_get(path, params, api_key):
    params = dict(params)
    params["key"] = api_key
    resp = requests.get(f"{API_BASE}/{path}", params=params, timeout=20)
    if resp.status_code != 200:
        try:
            detail = resp.json().get("error", {}).get("message", resp.text)
        except Exception:
            detail = resp.text
        print(f"ERROR: YouTube API {path} returned {resp.status_code}: {detail}")
        if resp.status_code == 403:
            print("Hint: check the key is valid, YouTube Data API v3 is enabled on the project, "
                  "and the daily quota (10,000 units) isn't exhausted.")
        sys.exit(1)
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="Search YouTube for a niche/keyword via the official Data API v3.")
    parser.add_argument("query", help="Search query / niche keyword")
    parser.add_argument("--limit", type=int, default=25, help="Max results (up to 50 per API call, default 25)")
    parser.add_argument("--order", default="relevance",
                         choices=["relevance", "viewCount", "date", "rating"],
                         help="Sort order (default relevance)")
    parser.add_argument("--published-after", default=None, help="Only videos published after this date (YYYY-MM-DD)")
    parser.add_argument("--region", default=None, help="2-letter region code, e.g. RU, US")
    parser.add_argument("--lang", default=None, help="Relevance language, e.g. ru, en")
    args = parser.parse_args()

    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("ERROR: YOUTUBE_API_KEY is not set.")
        print("Get a free key: console.cloud.google.com -> enable 'YouTube Data API v3' -> Credentials -> API key.")
        sys.exit(1)

    limit = max(1, min(args.limit, 50))

    search_params = {
        "part": "snippet",
        "q": args.query,
        "type": "video",
        "maxResults": limit,
        "order": args.order,
    }
    if args.published_after:
        search_params["publishedAfter"] = f"{args.published_after}T00:00:00Z"
    if args.region:
        search_params["regionCode"] = args.region
    if args.lang:
        search_params["relevanceLanguage"] = args.lang

    print(f"\n  Searching YouTube (Data API v3) for: \"{args.query}\"")
    print(f"  order={args.order}  limit={limit}" +
          (f"  since={args.published_after}" if args.published_after else "") + "\n")

    search_data = api_get("search", search_params, api_key)  # costs 100 quota units
    items = search_data.get("items", [])
    if not items:
        print("  No results found.")
        return

    video_ids = [it["id"]["videoId"] for it in items if it.get("id", {}).get("videoId")]
    channel_ids = list({it["snippet"]["channelId"] for it in items})

    # 1 quota unit each, batched
    videos_data = api_get("videos", {
        "part": "statistics,contentDetails,snippet",
        "id": ",".join(video_ids),
    }, api_key)
    channels_data = api_get("channels", {
        "part": "statistics",
        "id": ",".join(channel_ids),
    }, api_key)

    channel_subs = {
        c["id"]: int(c["statistics"].get("subscriberCount", 0)) if not c["statistics"].get("hiddenSubscriberCount") else None
        for c in channels_data.get("items", [])
    }

    rows = []
    for v in videos_data.get("items", []):
        stats = v.get("statistics", {})
        views = int(stats.get("viewCount", 0))
        channel_id = v["snippet"]["channelId"]
        subs = channel_subs.get(channel_id)
        engagement = round(views / subs, 2) if subs and subs > 0 else None
        rows.append({
            "title": v["snippet"]["title"],
            "url": f"https://www.youtube.com/watch?v={v['id']}",
            "channel": v["snippet"]["channelTitle"],
            "channel_url": f"https://www.youtube.com/channel/{channel_id}",
            "subs": subs,
            "views": views,
            "likes": int(stats.get("likeCount", 0)) if "likeCount" in stats else None,
            "comments": int(stats.get("commentCount", 0)) if "commentCount" in stats else None,
            "duration": format_duration(parse_iso8601_duration(v["contentDetails"]["duration"])),
            "published": v["snippet"]["publishedAt"][:10],
            "engagement_ratio": engagement,  # views / subscribers — outlier signal
        })

    # Outliers first: high views relative to channel size are the interesting signal for niche research
    rows.sort(key=lambda r: (r["engagement_ratio"] is None, -(r["engagement_ratio"] or 0)))

    for i, r in enumerate(rows, 1):
        print(f"  {i}. {r['title']}")
        print(f"     {r['url']}")
        print(f"     Channel: {r['channel']} ({human_number(r['subs'])} subs) — {r['channel_url']}")
        eng = f"{r['engagement_ratio']}x subs" if r['engagement_ratio'] is not None else "N/A"
        print(f"     Views: {human_number(r['views'])}  |  Engagement: {eng}  |  "
              f"Duration: {r['duration']}  |  Published: {r['published']}")
        if r["likes"] is not None or r["comments"] is not None:
            print(f"     Likes: {human_number(r['likes'])}  Comments: {human_number(r['comments'])}")
        print(f"     {'-' * 70}")

    print(f"\n  Quota used: ~{100 + 2} units this call "
          f"(search=100, videos.list=1, channels.list=1) out of the 10,000/day free budget.\n")


if __name__ == "__main__":
    main()
