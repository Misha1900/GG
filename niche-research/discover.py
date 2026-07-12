import json, os, sys, traceback
import yt

SP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SP, "raw", "search")
os.makedirs(OUT, exist_ok=True)

subs = json.load(open(os.path.join(SP, "subniches.json")))
done, failed = 0, []
for niche, sn_map in subs.items():
    for sn, cfg in sn_map.items():
        fname = os.path.join(OUT, f"{niche}__{sn}.json")
        if os.path.exists(fname):
            continue
        try:
            d = yt.search_videos(cfg["q"], cfg["dur"])
            json.dump(d, open(fname, "w"))
            done += 1
            print(f"OK {niche}/{sn}: {len(d.get('items', []))} videos | quota={yt.quota_used()}", flush=True)
        except RuntimeError as e:
            failed.append((niche, sn, str(e)[:200]))
            print(f"FAIL {niche}/{sn}: {e}", flush=True)
            if "QUOTA_EXCEEDED" in str(e):
                sys.exit(f"Quota exceeded after {done} searches")

print(f"\nDone: {done} new searches, quota used: {yt.quota_used()}")
if failed:
    print("Failures:", failed)
