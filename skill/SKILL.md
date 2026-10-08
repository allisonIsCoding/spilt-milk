---
name: milk-carton-schematics
description: Redraw, change and sanity-check the schematics for the BM Milk Carton, the 40 ft wood Burning Man art piece (a milk carton tipped over with a slide spilling from its spout and a railed staircase inside). Use this whenever the user mentions the milk carton, its tilt, spout, spill slide, puddle, the stairs, landings or stair width inside it, or asks for a plan, elevation, dimensions, or a "does this fit / is it too steep" check, even if they never say "schematic" or "skill". Also use it to answer what-if questions such as a different tilt or a wider stair, because the numbers come from a script, not from guessing.
---

# BM Milk Carton schematics

The project is a 40 ft wood-built, burnable milk carton tipped over and spilling. The spill is a slide. Inside is a railed zigzag staircase up to the spout. The geometry is easy to get wrong by hand (the earlier hand-drawn versions were wrong in several ways), so this skill bundles a small generator. Use it for every change instead of estimating, and report what it says, including when it says no.

## Workflow

1. **Know what is settled.** Read `references/design-decisions.md` the first time you use this skill in a conversation. It lists what the user decided, what was assumed, and what is open. Read `references/stair-analysis.md` before answering anything about stairs, and `references/open-questions.md` when the user asks what is left to do. Do not re-open settled decisions (50 degree tilt, spout in line with the ridge, slide shape, wood construction, zigzag stairs).
2. **Turn the request into parameters.** See the table below. Defaults reflect the latest decisions. If the user says their current setting differs from a default, trust the user and pass it explicitly.
3. **Run the generator** (Python 3, no dependencies for SVG):
   ```bash
   python scripts/run.py --set tilt_deg=45 --set stair_width_ft=4 --png --out /mnt/user-data/outputs/milk-carton
   ```
   Add `--sweep` for the stair width x landing interval table. `--png` needs `cairosvg` (`pip install cairosvg --break-system-packages`); skip it if that fails, the SVGs are the real output. Exit status 1 means a stair check failed, not that the script crashed: the drawings and `report.md` are still written, and the failure is the answer.
4. **Look at the PNG before presenting it** (use `view`). Confirm labels do not collide and nothing is clipped. If it looks wrong, fix the cause in `scripts/milk_carton/` rather than describing around it.
5. **Present** `elevation.svg` and `plan.svg` (plus PNGs if made) with `present_files`, then summarize in a few sentences: what changed, whether every check passes, and the two or three numbers that moved (spout height, slide steepness, worst stair pitch). Lead with any failure, in plain words.

## Parameters

| The user wants... | Parameter (default) | Notes |
|---|---|---|
| more or less tilt | `tilt_deg` (50) | Climbing surface slopes 90 minus tilt. Tested 45 to 55. |
| wider or narrower stairs | `stair_width_ft` (4.5) | Over about 4.7 ft cannot start at grade. |
| landings closer or farther apart | `landing_interval_ft` (4) | 3 fails on clearance, 5 gets steep. |
| a deeper (wider) carton | `width_ft` (16) | 18 makes the stairs gentler, not wider, and drifts from real proportions. |
| the carton sunk more or less | `sink_ft` (2.8) | Widens the V at grade, lowers the spout. |
| a gentler or steeper slide | `slide_run_ft` (23.75) | Longer run means gentler, but slowly: the steepest section goes about 67, 61, 55 degrees at 24, 32, 40 ft of run. The drop is set by the spout height. |
| taller rails or door | `rail_height_ft` (3.5), `door_height_ft` (6.5) | |
| proportions | `height_ft`, `body_ft`, `roof_ft` (40, 28, 9) | Fin is whatever remains. |
| spout shape | `beak_ft`, `mouth_len_ft`, `mouth_depth_ft` | |
| diagonal stair flights | `flight_skew_ft` (0) | Fails: see below. |

Repeat `--set key=value` for several changes. Use `--config <file.json>` to load a saved set (`assets/default.json` is the template).

## Reading the results

- The elevation shows the stairs end-on, so flights and landings appear stacked and overlapping. They sit at different depths across the carton; the plan view is the place to check them.
- Checks that can fail: stair pitch (35 degrees is the comfort limit, 38 the hard limit), clearance to the sloped surfaces, headroom where stair surfaces overlap in plan, whether the first flight fits the V at grade, and room for the launch deck.
- Why diagonal flights fail: each foot a flight advances along the carton raises the 40 degree floor under it by about 0.84 ft, so skew pushes the stairs into the floor. "Diagonal" in practice means flights run straight across the carton's depth, stacked along its length.
- The slide's steepest section is much steeper than a playground slide. Say so when it matters, and offer speed-control options from `references/open-questions.md`.

## Honesty about what this is

These are concept schematics for planning and for the Black Rock City honoraria letter of intent. Dimensions are scaled from a real half-gallon carton from memory. Structure, footings, the slide support, railing heights and baluster spacing need a structural engineer and BRC art safety. Say that whenever the user is about to treat a number as final. Slide supports and the entry door are placeholders.

## Hand-offs

- Photoreal images: use `references/image-prompts.md` for Gemini or other generators. This skill does not make them.
- Pushing to GitHub: not possible from chat. The project repo has `scripts/publish.sh`; the user runs it.
- Keeping this skill current: the generator lives in the project repo (`src/milk_carton`). When the user changes a decision, offer to update `config/default.json` there so the skill and repo agree.

## Changing the generator

All code is in `scripts/milk_carton/`: `config.py` (parameters), `geometry.py` (carton and slide), `stairs.py` (layout and checks), `elevation.py` and `plan.py` (drawings). If you change behavior, run a few `--set` combinations, view the output, and tell the user what you changed so they can mirror it in the repo.
