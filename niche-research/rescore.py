import json, os, re, glob
from datetime import datetime, timezone
from collections import defaultdict

SP = os.path.dirname(os.path.abspath(__file__))
NOW = datetime(2026, 7, 12, tzinfo=timezone.utc)
CUTOFF = datetime(2026, 1, 12, tzinfo=timezone.utc)
ALIVE_AFTER = datetime(2026, 6, 12, tzinfo=timezone.utc)   # последний ролик <= 30 дней назад
FRESH_AFTER = datetime(2026, 7, 2, tzinfo=timezone.utc)    # ролики моложе 10 дней ещё набирают
MIN_LONG = 180

uploads = json.load(open(os.path.join(SP, "raw/channels/uploads.json")))
vdet = json.load(open(os.path.join(SP, "raw/channels/video_details.json")))
chans = {c["id"]: c for c in json.load(open(os.path.join(SP, "raw/channels/all_channels.json")))}

chan_subniches = defaultdict(set)
for f in glob.glob(os.path.join(SP, "raw/search/*.json")):
    tag = os.path.basename(f)[:-5]
    for it in json.load(open(f)).get("items", []):
        chan_subniches[it["snippet"]["channelId"]].add(tag)

def pdt(s): return datetime.fromisoformat(s.replace("Z", "+00:00"))

LAT = re.compile(r"[A-Za-z]")
NONLAT = re.compile(r"[ऀ-ॿঀ-৿؀-ۿЀ-ӿ一-鿿぀-ヿ가-힯฀-๿֐-׿஀-௿ఀ-౿਀-੿ഀ-ൿ]")
HINGLISH = re.compile(r"\b(hai|nahi|kya|kaise|karo|kare|wala|paise|kamao|tarika|sikho|banao|hoga|sabse|jyada|lakh|crore|rupay|paisa)\b", re.I)
def is_en(d):
    if d["lang"]: return d["lang"].split("-")[0] == "en"
    txt = d["title"] + " " + d["desc"][:200]
    return not NONLAT.search(txt) and not HINGLISH.search(d["title"]) and bool(LAT.search(txt))

rows = []
for cid, vids in uploads.items():
    c = chans.get(cid)
    if not c: continue
    st = c.get("statistics", {})
    if st.get("hiddenSubscriberCount"): continue
    subs = int(st.get("subscriberCount", 0))
    if subs >= 50000: continue
    longs = []
    for v in sorted(vids, key=lambda x: x["published"] or "", reverse=True):
        d = vdet.get(v["vid"])
        if d and d["dur"] > MIN_LONG:
            longs.append((v["vid"], d))
    if len(longs) < 10: continue                      # 10+ длинных за 6 мес
    last10 = longs[:10]
    newest = pdt(last10[0][1]["published"])
    alive = newest >= ALIVE_AFTER
    # свежестная поправка: молодые (<10 дн) недобравшие не в знаменателе
    qual = [(vid, d) for vid, d in last10
            if d["views"] >= 30000 or pdt(d["published"]) <= FRESH_AFTER]
    if len(qual) < 6: continue
    n30 = sum(1 for _, d in qual if d["views"] >= 30000)
    success = n30 / len(qual) >= 0.7
    views10 = [d["views"] for _, d in last10]
    en = sum(1 for _, d in last10 if is_en(d)) >= 7
    total6mo = sum(d["views"] for _, d in longs)
    rows.append({
        "id": cid, "title": c["snippet"]["title"], "subs": subs,
        "created": c["snippet"]["publishedAt"][:10],
        "last_video": last10[0][1]["published"][:10],
        "alive": alive, "success": success, "english": en,
        "n30": n30, "den": len(qual),
        "median": sorted(views10)[5], "total_6mo_views": total6mo,
        "n_longs_6mo": len(longs),
        "subniches": sorted(chan_subniches.get(cid, [])),
        "last10": [{"vid": vid, "t": d["title"][:90], "pub": d["published"][:10],
                    "v": d["views"], "m": d["dur"]//60} for vid, d in last10],
    })

json.dump(rows, open(os.path.join(SP, "rescore_results.json"), "w"))
alive_all = [r for r in rows if r["alive"]]
winners = [r for r in alive_all if r["success"] and r["english"]]
print(f"Каналов с 10+ длинными за 6 мес: {len(rows)}")
print(f"Живых сейчас (ролик за 30 дней): {len(alive_all)}")
print(f"ЖИВЫХ УСПЕШНЫХ (>=70% свежих >=30k, en): {len(winners)}")
print()

# рейтинг подниш
agg = defaultdict(lambda: {"alive": 0, "win": [], "meds": []})
base = lambda tag: tag.split("__r")[0]
for r in alive_all:
    for tag in set(base(t) for t in r["subniches"]):
        a = agg[tag]
        a["alive"] += 1
        a["meds"].append(r["median"])
        if r["success"] and r["english"]:
            a["win"].append(r)

print(f"{'подниша':40} {'жив':>4} {'усп':>4} {'плотн':>6} {'мед.усп':>9} {'сумм.просм.усп 6мес':>14}")
out = []
for tag, a in agg.items():
    w = a["win"]
    med_w = sorted(x["median"] for x in w)[len(w)//2] if w else 0
    tot_w = sum(x["total_6mo_views"] for x in w)
    dens = len(w)/a["alive"] if a["alive"] else 0
    out.append((tag, a["alive"], len(w), dens, med_w, tot_w))
out.sort(key=lambda x: (-x[2], -x[4]))
for t in out:
    if t[2] or t[1] >= 8:
        print(f"{t[0][:40]:40} {t[1]:4} {t[2]:4} {t[3]:6.0%} {t[4]:9,} {t[5]:14,}")

print("\n=== ЖИВЫЕ УСПЕШНЫЕ КАНАЛЫ ===")
for r in sorted(winners, key=lambda x: -x["median"]):
    print(f"{r['title'][:38]:38} subs={r['subs']:6} last={r['last_video']} {r['n30']}/{r['den']} med={r['median']:8,} 6mo={r['total_6mo_views']:11,} {r['subniches'][:2]}")
