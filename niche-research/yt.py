import json, os, time, urllib.request, urllib.parse

BASE = "https://www.googleapis.com/youtube/v3"
SP = os.path.dirname(os.path.abspath(__file__))
KEY = os.environ.get("YOUTUBE_API_KEY") or open(os.path.join(SP, "yt_key")).read().strip()
QUOTA_FILE = os.path.join(SP, "quota.json")
PUBLISHED_AFTER = "2026-01-12T00:00:00Z"

def _quota():
    if os.path.exists(QUOTA_FILE):
        return json.load(open(QUOTA_FILE))
    return {"used": 0}

def _add_quota(n):
    q = _quota()
    q["used"] += n
    json.dump(q, open(QUOTA_FILE, "w"))
    return q["used"]

def call(endpoint, cost, **params):
    params["key"] = KEY
    url = f"{BASE}/{endpoint}?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=40) as r:
                data = json.load(r)
            _add_quota(cost)
            return data
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:500]
            if e.code in (403, 429) and ("quota" in body.lower() or "rateLimit" in body):
                raise RuntimeError(f"QUOTA_EXCEEDED: {body}")
            if e.code >= 500 and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"HTTP {e.code}: {body}")
        except Exception:
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise

def search_videos(q, duration, max_results=50, order="viewCount"):
    return call("search", 100, part="snippet", type="video", q=q,
                publishedAfter=PUBLISHED_AFTER, relevanceLanguage="en",
                regionCode="US", order=order, maxResults=max_results,
                videoDuration=duration)

def chunks(lst, n=50):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def channels_list(ids):
    out = []
    for ch in chunks(ids):
        d = call("channels", 1, part="snippet,statistics,contentDetails",
                 id=",".join(ch), maxResults=50)
        out += d.get("items", [])
    return out

def uploads_recent(playlist_id, n=20):
    d = call("playlistItems", 1, part="snippet,contentDetails",
             playlistId=playlist_id, maxResults=min(n, 50))
    return d.get("items", [])

def videos_list(ids):
    out = []
    for ch in chunks(ids):
        d = call("videos", 1, part="snippet,statistics,contentDetails",
                 id=",".join(ch), maxResults=50)
        out += d.get("items", [])
    return out

def quota_used():
    return _quota()["used"]
