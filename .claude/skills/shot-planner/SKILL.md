---
name: shot-planner
description: Use when a finished narrative script (like SCRIPT_MAP.md) needs to become a concrete production plan — exact timing per shot, visual source, voiceover line, TTS voice + intonation, and which tool builds each asset. Triggers on "распиши по кадрам", "визуальный план", "план производства", "shot list", "storyboard", "раскадровка".
---

# Shot Planner

Turns a written script into a shot-by-shot production plan the team (or the AI tools) can actually execute against. This is the bridge between "the script is good" and "footage exists."

## Input

A script already broken into numbered shots with a visual-type tag, in the style already used in `SCRIPT_MAP.md`:

```
**S1+S2** — 🎙 Lipsync
- EN: ...
- RU: ...
```

If the script isn't shot-tagged yet, tag it first (see "Tagging a raw script" below) — don't skip straight to timing without this step.

## Output: one row per shot

For every shot, produce:

| Field | What it captures |
|---|---|
| **ID** | Matches the script's shot numbering (S1, S12, S44b…) — never renumber, always traceable back to the script. |
| **Timecode** | Start–end in the final edit, e.g. `00:04–00:07`. Estimate duration from spoken word count (RU ≈ 2.2 words/sec at documentary pace, EN ≈ 2.3–2.5 words/sec) or from the visual beat if there's no VO on that shot. Running total must match the target runtime — flag drift early, don't discover it in the edit. |
| **Visual** | Concrete description of what's on screen — not just the type tag. "🎬 Animation" becomes "3D render: chain-link fence, low angle, Conley vaulting it, motion blur on the far leg." Specific enough that whoever builds it doesn't have to re-invent the shot. |
| **Source/Tool** | Which pipeline builds this asset (see "Routing to tools" below). |
| **VO / on-screen text** | The exact line(s) that play under this shot, RU + EN if both are shipped. |
| **Voice + intonation** | Which voice profile, and direction on delivery: pace (slow/measured vs urgent), register (narrator calm vs confrontational), where the emphasis word sits, where a pause lands, whether it's a question that should lift at the end. Don't just say "serious" — say what changes moment to moment: "flat and clinical on the statistic, then a half-second pause before the gut-punch clause." |
| **Status** | `planned` → `asset requested` → `generated` → `approved` → `in edit`. Update as you go; this is the single source of truth for what's left to build. |

## Tagging a raw script (if not already done)

Reuse this project's existing legend — don't invent a new one:
- 🎙 **Lipsync** — narrator speaks to camera (avatar/talking-head).
- 🎬 **Animation** — 3D or illustrated b-roll built for this script.
- 📊 **Graphics** — motion graphics / kinetic typography / data viz (built in Remotion — see the `remotion-graphics` skill).
- 🎞 **Footage** — real/stock/archival video.

Rule of thumb already established in this project: **no more than 2 of the same type in a row**, except where breaking that rule is a deliberate dramatic choice (an unbroken run of real footage for a "this really happened" moment; an unbroken run of lipsync for the emotional climax). If you find yourself defaulting to the same tag for 4+ shots in a row without a stated reason, that's a flag — vary the visual language or justify the exception explicitly, the same way `SCRIPT_MAP.md` already does in its "Исключения намеренные" notes.

## Routing to tools

Match each shot's asset need to what's actually available, cheapest/fastest first:

- **Lipsync / talking-head avatar** → Higgsfield avatar/lipsync tools (already connected in this session).
- **3D / stylized animation b-roll** → Higgsfield `generate_video` / `generate_3d` / `motion_control`, or Remotion if it's really a graphics composition wearing an "animation" label.
- **AI still images** (portraits, key art, textures to animate in Remotion) → Higgsfield `generate_image` (or an external model like GPT Image / NanoBanana if the user names one specifically).
- **Motion graphics / kinetic type / data viz / stat callouts** → Remotion (see `remotion-graphics` skill) — this is code, not a generation call, so budget dev time not just render time.
- **Real footage** → search first (stock libraries, archival, or footage the user already has in the repo — check `renders/` and any raw-footage folders before generating something that already exists) before generating or paying for it.
- **Voiceover** → Higgsfield / vidIQ voiceover tools; note the requested voice + intonation direction from the plan above in the generation prompt verbatim, don't paraphrase it away.
- **Music / SFX / b-roll** → vidIQ `generate_music` / `generate_broll`.

## Keeping dramaturgy intact through production

The shot plan must not flatten the pacing the script worked hard to build:
- Carry over the Act structure and its emotional curve from the script — annotate each Act's target feeling at the top of its block (tense / playful / dread / triumphant) so whoever builds the assets for that Act calibrates tone, not just content.
- If `reference-analysis` was run on comparable channels, cite the specific reference pattern being matched next to shots where it applies ("open-loop payoff shot — match the delayed-reveal pacing from ref #2").
- Timing drift is a dramaturgy bug, not just a technical one — a beat that runs long because the VO is slow kills the "but/therefore" rhythm from the `storytelling` skill. Re-check word count against the timecode whenever a line is rewritten.

## Workflow

1. Confirm the script is shot-tagged (tag it if not).
2. Walk shots in order, filling every field above — don't batch "I'll do timing later," timing drift compounds.
3. Flag any run of 3+ identical visual types that isn't a stated exception.
4. Produce the routing column against currently connected tools (Higgsfield, vidIQ, Remotion) — don't invent a tool that isn't set up.
5. Output as a table (or update `SCRIPT_MAP.md` in place, extending its existing per-shot blocks with the new fields) — ask which the user wants before picking.
6. Track status per shot as production proceeds; surface a short "what's left" summary on request rather than making the user scan the whole table.
