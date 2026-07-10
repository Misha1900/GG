---
name: niche-search
description: Use when the user wants to search YouTube directly by topic/niche or find real videos/channels on a subject WITHOUT going through vidIQ — e.g. "проанализируй нишу психология", "найди видео про...", "какие каналы есть в нише...", "поищи на ютубе". Uses the free official YouTube Data API v3, independent of the vidIQ MCP tools.
---

# Niche Search

Goes to YouTube directly via the official, free **YouTube Data API v3** — deliberately *not* the connected vidIQ tools. Use this whenever the user asks for niche/topic research and doesn't want vidIQ in the loop.

## Setup (one-time)

Requires `YOUTUBE_API_KEY` in the environment:
1. console.cloud.google.com → create/select a project → enable **"YouTube Data API v3"**.
2. Credentials → Create credentials → API key. No billing account or credit card required — the free daily quota (10,000 units) applies automatically.
3. `export YOUTUBE_API_KEY=...` (or add it wherever this project's env vars live).

If the key is missing, tell the user exactly these steps before attempting a search — don't guess or fall back to a different data source silently.

**Environment note:** direct scraping approaches (yt-dlp, third-party transcript APIs) hit `youtube.com` / third-party hosts directly and may be blocked by network policy in a sandboxed session. This skill instead calls `googleapis.com`, which is reachable — confirm reachability once with a small test call if a prior attempt in the session failed unexpectedly.

## Running a search

```bash
python <skill-dir>/scripts/yt_niche_search.py "QUERY" [--limit 25] [--order relevance|viewCount|date|rating] [--published-after YYYY-MM-DD] [--region RU] [--lang ru]
```

For a Russian-language niche, pass `--lang ru` (and `--region RU` if geography matters) so results aren't dominated by English content.

Output per video: title, URL, channel + subscriber count, views, **engagement ratio (views ÷ subscribers)**, likes/comments, duration, publish date — sorted by engagement ratio descending. That ratio is the key niche-research signal: a video pulling far more views than its channel's subscriber count would predict is either a genuine outlier format or freshly boosted by the algorithm — both are useful data points.

## Quota discipline

`search.list` costs **100 of the 10,000 daily units** per call (not per result) — one call with `--limit 50` is far cheaper than five calls with `--limit 10`. `videos.list`/`channels.list` cost 1 unit each and are batched automatically by the script. Budget roughly:
- ~90 search calls/day if used alone, or
- fewer if combined with other quota use — don't run redundant searches for query variants that clearly overlap; pick 2-3 well-chosen queries per niche rather than a dozen near-duplicates.

## Turning results into a niche analysis

When asked to "analyze a niche" (not just find a few videos), run this workflow:

1. **2-3 query angles**, not one — a niche like "психология" needs variety: the bare topic, a format-specific angle ("психология разбор кейса"), and a Shorts/long-form split if relevant. Reusing near-duplicate queries wastes quota for no new signal.
2. **Pull with `--order viewCount`** for one pass (what's biggest) and `--order relevance` for another (what YouTube considers most on-topic) — they surface different things.
3. **Group by channel** across all pulled results — repeat appearances from the same channel signal a dominant player in the niche.
4. **Read the engagement-ratio column as the outlier signal**: a small channel with a video at 20x+ its subscriber count found a format or hook worth understanding — hand that specific video to the `reference-analysis` skill for a deep forensic pass rather than treating every result equally.
5. **Report the niche shape**, not just a video list: who the 3-5 dominant channels are, typical video length, upload cadence if inferable from publish dates in the sample, and 1-2 concrete outlier videos worth a deeper look.

## Handing off

- A standout video found here → `reference-analysis` for the detailed hook/arc/payoff breakdown.
- Patterns from the niche report → feed into `storytelling`/`viral-hooks` when drafting a script that needs to compete in that space.
