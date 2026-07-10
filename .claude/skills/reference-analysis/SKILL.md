---
name: reference-analysis
description: Use when the user shares reference YouTube videos or channels ("посмотри на этот канал", "разбери этот ролик", "хочу чтобы графика была как здесь") to set a concrete quality/style bar before or during scriptwriting and shot planning. Extracts the mechanics behind why a reference video works, not just a vibe description.
---

# Reference Analysis

Turns "I want it to feel like this channel" into a specific, actionable list the `storytelling`, `viral-hooks`, and `shot-planner` skills can act on. A vague "make it feel premium" is useless to a production plan; "3-second hard cuts, no dissolve transitions, all graphics on a dark navy field with one accent color" is.

## Inputs to gather first

- The video URL(s) or channel(s).
- What specifically the user wants to learn from it: writing (hooks/pacing), visuals (graphics style, editing rhythm), or both. Don't run a full forensic pass on visuals if they only asked about the hook.
- Use the connected vidIQ tools to pull real data where useful: `vidiq_video_transcript` (script text), `vidiq_video_stats` / `vidiq_channel_stats` (does it actually perform, or is it just aesthetically appealing?), `vidiq_video_watch` (visual pass). Don't analyze a video's mechanics without also checking whether it actually retained/performed — a beautiful video that flopped is a style reference, not a proof of a working formula.

## The 7-axis forensic pass (script/narrative side)

Run this on the transcript, timestamped where possible:

| Axis | What to extract |
|---|---|
| **Hook** | What lands in the first 1–3 seconds — visual and verbal? Which of the four hook killers (delay/confusion/irrelevance/disinterest — see `viral-hooks`) it avoids, and how. |
| **Narrative arc** | Where do setup / escalation / turn land, by timestamp? Map it against the classic 3-act shape. |
| **Emotion curve** | Sequence of emotional beats by timestamp — tension, relief, dread, humor, awe — in the order they're placed. |
| **Open loops** | Every "you'll see why in a second" / withheld payoff. Count them, note where each opens and where it closes. |
| **Silent/show-don't-tell beats** | Moments carried by visual or action alone, no narration — where do they use this and why (usually to let a real/dramatic moment breathe, same instinct behind this project's unbroken-footage exceptions). |
| **Payoff design** | What the ending delivers relative to what the hook promised. Does it recontextualize the opening (a "loop" ending)? |
| **Retention/virality signal** | Given the actual stats pulled via vidIQ, does the mechanic correlate with real performance, or is it just a stylistic choice this creator happens to use? Say which. |

Output the pass as a table with timestamps, not a prose summary — vague notes don't transfer into a shot plan.

## The visual/production pass (graphics side — when asked)

When the user wants "graphics that look this expensive," extract concretely, not impressionistically:
- **Cut rhythm** — average shot length, and where it deliberately breaks (long holds vs rapid cuts, and why each is used).
- **Color/grade** — palette, contrast, whether it's warm/cool/desaturated, consistency across shot types.
- **Typography** — font weight/style, motion-in/motion-out pattern for kinetic type, how much text is on screen at once.
- **Graphic language** — is data/stat visualization literal (charts) or stylized (abstract motion matching the number)? Consistency of a visual "system" (recurring icon style, recurring transition type) across the video — this consistency, more than any single flashy shot, is usually what reads as "expensive."
- **Transitions** — hard cuts vs motion-linked transitions (object in shot A becomes object in shot B) — the latter reads as higher-budget and is a good target for the `remotion-graphics` skill to replicate.

## Adapting, not copying

The point of this analysis is to raise the bar on *this* project's own script and shot plan — not to clone the reference. When feeding findings back in:
- Name the specific mechanic, not the source ("open-loop payoff, closes 40s later" not "do it like channel X").
- Flag mechanics that don't fit this project's actual content (a reference built for a 60s vertical short doesn't transfer wholesale to a 10-minute longform documentary act structure) — note the mismatch instead of forcing it.
- If several references are supplied, look for the mechanic that repeats across them — a pattern seen in 3 independent top performers is a stronger signal than one video's idiosyncrasy.

## Workflow

1. Confirm which axis (script, visual, or both) the user actually wants analyzed.
2. Pull transcript/stats via vidIQ tools; watch the video for the visual pass.
3. Run the relevant table(s) above with timestamps.
4. Translate findings into 3–6 concrete, applicable notes — feed them to `storytelling`/`viral-hooks` for script work, or to `shot-planner`/`remotion-graphics` for the production plan.
5. If findings conflict with an existing choice already locked into the script or shot plan, flag the conflict explicitly rather than silently overriding it.
