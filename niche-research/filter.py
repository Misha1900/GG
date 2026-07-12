import json, os, glob, re, sys
from datetime import datetime, timezone
import yt

SP = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(SP, "raw")
os.makedirs(os.path.join(RAW, "channels"), exist_ok=True)
CUTOFF = datetime(2026, 1, 12, tzinfo=timezone.utc)
MIN_LONG_SEC = 180

def parse_dur(iso):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m: return 0
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s

def parse_dt(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

# ---- Stage A: aggregate channels from search results
chan_subniches = {}
for f in glob.glob(os.path.join(RAW, "search", "*.json")):
    tag = os.path.basename(f)[:-5]
    for it in json.load(open(f)).get("items", []):
        cid = it["snippet"]["channelId"]
        chan_subniches.setdefault(cid, set()).add(tag)
chan_subniches = {k: sorted(v) for k, v in chan_subniches.items()}
print(f"Unique channels from search: {len(chan_subniches)}")

# ---- Stage B: channel stats
CH_FILE = os.path.join(RAW, "channels", "all_channels.json")
if os.path.exists(CH_FILE):
    channels = json.load(open(CH_FILE))
else:
    channels = yt.channels_list(list(chan_subniches))
    json.dump(channels, open(CH_FILE, "w"))
print(f"Channel records: {len(channels)} | quota={yt.quota_used()}")

small = []
for c in channels:
    st = c.get("statistics", {})
    if st.get("hiddenSubscriberCount"): continue
    subs = int(st.get("subscriberCount", 0))
    vids = int(st.get("videoCount", 0))
    if subs < 50000 and vids >= 10:
        small.append(c)
print(f"Small channels (<50k subs, >=10 videos): {len(small)}")

# ---- Stage C: recent uploads for each small channel
UP_FILE = os.path.join(RAW, "channels", "uploads.json")
uploads = json.load(open(UP_FILE)) if os.path.exists(UP_FILE) else {}
for i, c in enumerate(small):
    cid = c["id"]
    if cid in uploads: continue
    pl = c["contentDetails"]["relatedPlaylists"]["uploads"]
    try:
        items = yt.uploads_recent(pl, 50)
    except RuntimeError as e:
        if "QUOTA_EXCEEDED" in str(e):
            json.dump(uploads, open(UP_FILE, "w")); sys.exit(f"QUOTA at {i}")
        items = []
    uploads[cid] = [{"vid": x["contentDetails"]["videoId"],
                     "published": x["contentDetails"].get("videoPublishedAt") or x["snippet"]["publishedAt"]}
                    for x in items]
    if i % 200 == 0:
        json.dump(uploads, open(UP_FILE, "w"))
        print(f"  uploads {i}/{len(small)} quota={yt.quota_used()}", flush=True)
json.dump(uploads, open(UP_FILE, "w"))
print(f"Uploads fetched for {len(uploads)} channels | quota={yt.quota_used()}")

# ---- Stage D: video details. Need durations for last uploads (to find 10 last LONG videos)
# Only fetch videos published after CUTOFF minus small margin: if a channel's recent uploads
# are older than cutoff it can't pass anyway; fetch details only for videos >= CUTOFF,
# but ALSO we must detect "10th long video within 6 months" -> we only care about long videos
# after cutoff; if channel has <10 long after cutoff, it fails. So fetching post-cutoff only is enough.
need_vids = []
for cid, vids in uploads.items():
    for v in vids:
        if v["published"] and parse_dt(v["published"]) >= CUTOFF:
            need_vids.append(v["vid"])
need_vids = list(dict.fromkeys(need_vids))
print(f"Videos to fetch (post-cutoff): {len(need_vids)}")

VD_FILE = os.path.join(RAW, "channels", "video_details.json")
vdet = json.load(open(VD_FILE)) if os.path.exists(VD_FILE) else {}
missing = [v for v in need_vids if v not in vdet]
for batch in yt.chunks(missing, 50):
    try:
        for it in yt.videos_list(batch):
            sn, st, cd = it["snippet"], it.get("statistics", {}), it.get("contentDetails", {})
            vdet[it["id"]] = {
                "ch": sn["channelId"], "title": sn["title"],
                "desc": sn.get("description", "")[:600],
                "tags": sn.get("tags", [])[:15],
                "published": sn["publishedAt"],
                "lang": sn.get("defaultAudioLanguage") or sn.get("defaultLanguage") or "",
                "dur": parse_dur(cd.get("duration")),
                "views": int(st.get("viewCount", 0)),
                "likes": int(st.get("likeCount", 0) or 0),
                "comments": int(st.get("commentCount", 0) or 0),
            }
    except RuntimeError as e:
        json.dump(vdet, open(VD_FILE, "w"))
        sys.exit(f"QUOTA/ERR during videos: {e}")
json.dump(vdet, open(VD_FILE, "w"))
print(f"Video details: {len(vdet)} | quota={yt.quota_used()}")

# ---- Stage E: apply user criteria per channel
LAT = re.compile(r"[A-Za-z]")
NONLAT = re.compile(r"[ऀ-ॿঀ-৿؀-ۿЀ-ӿ一-鿿぀-ヿ가-힯฀-๿֐-׿஀-௿ఀ-౿਀-੿ഀ-ൿ]")
HINGLISH = re.compile(r"\b(hai|nahi|kya|kaise|karo|kare|wala|paise|kamao|tarika|sikho|banao|hoga|sabse|jyada|lakh|crore|rupay|paisa)\b", re.I)

def is_english(v):
    if v["lang"]:
        return v["lang"].split("-")[0] == "en"
    txt = v["title"] + " " + v["desc"][:200]
    if NONLAT.search(txt): return False
    if HINGLISH.search(v["title"]): return False
    return bool(LAT.search(txt))

ch_by_id = {c["id"]: c for c in small}
results = []
for cid, vids in uploads.items():
    # last long-form videos (post-cutoff details only; videos w/o details are pre-cutoff)
    longs = []
    for v in sorted(vids, key=lambda x: x["published"] or "", reverse=True):
        d = vdet.get(v["vid"])
        if d is None:  # pre-cutoff -> stop counting further, channel timeline goes older
            continue
        if d["dur"] > MIN_LONG_SEC:
            longs.append((v["vid"], d))
    last10 = longs[:10]
    if len(last10) < 10:
        continue  # fewer than 10 long videos within 6 months -> fails activity criterion
    views = [d["views"] for _, d in last10]
    n30 = sum(1 for x in views if x >= 30000)
    en = sum(1 for _, d in last10 if is_english(d))
    med = sorted(views)[5]
    c = ch_by_id[cid]
    results.append({
        "id": cid,
        "title": c["snippet"]["title"],
        "subs": int(c["statistics"].get("subscriberCount", 0)),
        "created": c["snippet"]["publishedAt"][:10],
        "country": c["snippet"].get("country", ""),
        "total_videos": int(c["statistics"].get("videoCount", 0)),
        "n30": n30, "median_views": med, "min_views": min(views), "max_views": max(views),
        "en10": en,
        "passes": n30 >= 7,
        "english": en >= 7,
        "subniches_found_in": chan_subniches.get(cid, []),
        "last10": [{"vid": vid, "title": d["title"], "published": d["published"][:10],
                    "views": d["views"], "dur": d["dur"], "lang": d["lang"]} for vid, d in last10],
    })

results.sort(key=lambda r: (-r["passes"], -r["median_views"]))
json.dump(results, open(os.path.join(SP, "channel_results.json"), "w"))
act = [r for r in results]
p = [r for r in results if r["passes"]]
pe = [r for r in p if r["english"]]
print(f"\nActive channels (10 long videos in 6mo): {len(act)}")
print(f"Passing 70%>=30k: {len(p)} | of them English: {len(pe)}")
print(f"Final quota used: {yt.quota_used()}")
