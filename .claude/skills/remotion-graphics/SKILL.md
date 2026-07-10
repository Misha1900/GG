---
name: remotion-graphics
description: Use when building the 📊 Graphics (motion graphics / kinetic typography / data viz) shots from the shot plan into actual Remotion React compositions. Triggers on "сделай графику", "Remotion", "kinetic typography", "анимированная статистика", "motion graphics".
---

# Remotion Graphics

Builds the 📊 Graphics shot type from `shot-planner` into render-ready Remotion compositions. This project doesn't need a full paid media-generation stack for this — Remotion here is a code target for graphics that are typography, data viz, and stylized motion, not AI-generated footage (that's Higgsfield's job).

## Scope

**In scope for this skill:** kinetic typography, animated statistics/counters, diagrams, icon-driven explainer graphics, transitions between shot types, lower thirds, on-screen text overlays.

**Not in scope — route elsewhere:** photoreal AI video/images (Higgsfield), lipsync/avatar (Higgsfield), stock/real footage (search first, check `renders/` and existing project assets before generating anything new).

## Composition conventions for this project

- One Remotion composition per shot ID (`S10_graphics`, `S29_diagram`, matching the naming already used in `renders/`) — keep the 1:1 mapping to the shot plan so status tracking stays accurate.
- Pull timing directly from the shot plan's timecode column — don't eyeball duration in the composition, derive `durationInFrames` from the planned timecode so drift shows up immediately if the VO changes.
- Match the project's visual language from `reference-analysis` findings if any are on file — consistent palette, consistent type treatment, consistent motion-in/motion-out curve across every graphics shot is what makes a whole video read as "expensive," not any single flashy composition.
- Default motion principle: **ease, don't linear** — spring physics or eased curves for anything meant to feel premium; linear interpolation reads as cheap/robotic almost universally.

## Build loop

1. Read the shot's plan row: visual description, VO line and its timing, any reference-analysis notes tagged to it.
2. Scaffold the composition (if the Remotion project isn't already set up, confirm root/structure with the user first rather than assuming a layout).
3. Write the component: text/graphic elements timed to the VO's emphasis points from the shot plan's "voice + intonation" column — a stat should land visually right as the VO says the number, not before or after.
4. Preview (`npm run dev`) before declaring it done — don't hand back a composition that's only been read, not watched.
5. Update the shot's status in the shot plan (`generated` → `approved` after the user signs off).

## When the user wants generation, not just code

If a graphics shot actually needs generated imagery/video composited into the Remotion scene (e.g., a stylized background plate), generate the asset via Higgsfield first, then bring the output file into the composition — don't try to generate media through Remotion itself, it's a renderer, not a generation tool.

## Note on `remotion-superpowers`

There's a popular community plugin (`remotion-superpowers`) that bundles Remotion with five paid MCP services (KIE, TwelveLabs, Pexels, ElevenLabs, Replicate) for footage search, video analysis, voiceover, and music generation, installed via `/plugin marketplace add`. It's not installed here because it substantially duplicates capability already covered by the connected Higgsfield and vidIQ tools (image/video generation, voiceover, music, b-roll) without the extra subscriptions. Revisit it only if a specific capability is missing that Higgsfield/vidIQ genuinely don't cover (e.g., TwelveLabs-style semantic search over existing raw footage) — install it deliberately for that gap, not wholesale.
