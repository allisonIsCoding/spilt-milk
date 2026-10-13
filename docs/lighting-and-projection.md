# Lighting and projection

Notes from a call with Tyler, a lighting expert, on Oct 13, 2026 (PT). These are his
recommendations from the call, cleaned up and grouped by topic. **Nothing has been bought.**
Where something has been checked since the call, the note says so. Items that conflict
with an earlier decision are flagged here and in `open-questions.md`. They have not
been changed.

## Summary

- Only light the piece at night. Use uplighting: wash lights on the ground, aimed up the
  carton, with the glare side hidden behind a shield.
- Projection map the carton at night with Resolume **Arena**, not Avenue.
- Power needs are small. **The plan is solar.** Tyler's 4 kW generator figure is only a
  reference point for sizing.
- Rough cost: about $500 for lights and cords, about $3,000 for two projectors (used if
  possible), Resolume, and a computer to run it.
- Next step: build a tiny prototype.

## Power

- **Decided: solar.** The team has more experience with solar than with generators.
  This matches the "solar lighting" line in `budget.md`.
- Tyler said the lighting doesn't draw much. He suggested a 4 kW generator, which he
  thought would be more than enough. (When we said solar, he joked, "eco milk.") Use
  4 kW only as an upper-bound reference. Size the solar system from the real load.
- Rough load to size against: the Govee flood light sets are listed at 72 W per 6
  pack. Add the projectors and the computer, which will draw much more. Use each
  projector's spec sheet. Multiply by the hours of darkness each night.
- The timer and the Govee power adapters plug into regular 120 V outlets. The solar
  setup needs an inverter that stays on all night.

## Lighting the outside

- **Night only.** Don't plan daytime lighting.
- **Uplighting.** Put the lights at the base and aim them up the carton walls.
- **Wash lights: Govee Outdoor Flood Lights 2.** Tyler recommends these. They come as
  a daisy-chained set ([product page](https://us.govee.com/products/outdoor-flood-lights?variant=44604067184825)).
  Checked on the Govee US site on Oct 13, 2026:
  - Model H7058 (6 pack) is $179.99. Model H7057 (4 pack) is $119.99.
  - Each light is over 1,000 lm. White runs from 2700K to 6500K, plus RGBIC color.
  - Runs on 24 V. The listed wattage is 72 W for the set.
  - Weather ratings: lights IP66, control box IP65, power adapter only IP44.
    Rated for -20°C to 45°C.
  - Controlled over Wi-Fi and Bluetooth through the Govee app, Matter, Alexa, or Google.
  - **For the playa:** there's no Wi-Fi out there. Check that the on/off schedule runs
    without the cloud, or rely on the plug-in dusk-to-dawn timer below. The IP44 adapter
    needs a dust cover. Lights sitting in the daytime sun may run past the 45°C rating.
- **Hide the fixture, show the light.** On the ground, cover the side of each light that
  people would see. Use an L-shaped piece of plywood, or pieces that look like plastic milk
  cartons. People should see the light on the carton, not the bulb.
- **Dusk-to-dawn timer: UltraPro Photocell Timer, model 86940-T1.** Tyler recommends
  this one ([Home Depot](https://www.homedepot.com/p/UltraPro-Photocell-Timer-Dusk-to-Dawn-2-Grounded-Outlet-2-4-6-8-hour-On-Off-Button-Outdoor-86940-T1/336144053)).
  It is a plug-in outdoor timer with a light sensor and two grounded outlets. It can
  run dusk to dawn, or count down 2, 4, 6, or 8 hours from dusk. It has an on/off
  button. Home Depot listed it at $11.98 in a search result on Oct 13, 2026. The
  product page blocked a direct check.
  - Aim the light sensor away from the uplights and the projector. If the piece's own
    light reaches the sensor, the timer can read that as daylight and turn
    everything off.
- **Before the burn:** take out the lights, cords, shields, projectors, and the computer.
  Plastic shields and glued plywood are on the do-not-burn list in `materials.md`.

## Inside ideas

Tyler's ideas for the inside. None of them is decided.

- Milk-themed chandeliers.
- Big glowing cow udders.
- A milk fountain.
- More wash lights inside.
- A *Clockwork Orange* milk bar (the Korova Milk Bar look).

## Projection mapping

### Software: Resolume Arena

- How it works: a standard 16:9, 1080p video file goes in. In the editor you draw shapes
  ("slices") over the parts of the carton you want to hit. Then you route the video to
  each shape.
- **Buy Arena, not Avenue.** Checked on resolume.com on Oct 13, 2026: projection
  mapping (warping slices to fit a surface), edge blending, and DMX are Arena-only.
  Avenue can't warp its output. If someone buys Avenue by mistake, upgrading costs
  only the difference.
- **Price.** Tyler said "$600-ish, $300 with the discount." Resolume's site lists Arena at
  **€799** for one computer, about $895. Avenue is €299. Resolume says it often runs
  a Black Friday sale. Tyler said it's 50% off. Black Friday 2026 is **Fri Nov 27**.
  At 50% off, Arena is about €400, roughly $450. Check the real price then.
- You also need **a computer to run Resolume**. It isn't priced yet.

### Placing the projector

- Pick a spot and **don't move the projector after mapping.** The mapping is tied to that
  exact position.
- Any angle works: off to the side, from above, or from below. The software corrects for it.
- If it sits on the ground aimed at the side of the carton, raise it above head height so
  people don't walk through the beam. One idea is to mount it on a small milk carton
  tall enough to put the lens above people's heads.
- With an ultra-short-throw projector, a small shelf just above or below the image may be
  enough.

### Choosing a projector

- **Brightness:** 5,000 to 7,000 lumens is probably good.
- **Resolution:** 1080p is fine.
- **Size it to the target.** Find the biggest dimension of what you want to map (the
  child's face, for example). The image has to cover that.
- **Put the projector as close as you can.** Use the throw ratio to work out how close
  it can go.
  - The rule of thumb: throw distance = throw ratio × image width. A 1080p image is
    16:9, so if height limits you, the image width is the height × 16/9.
  - Example only, not a measurement: an image 8 ft wide needs about 12 ft at a
    standard 1.5:1 throw. A 0.5:1 short throw needs about 4 ft. A 0.25:1
    ultra-short throw needs about 2 ft.
  - Closer means a smaller throw and a brighter image for the same lumens.
- **Look at short-throw projectors.** An **older long-throw projector** is also an option,
  and probably cheap used (Facebook Marketplace, for example).

### Dust

- Dust will be the main problem. Every projector has a lens and an opening the light
  comes out of. **Dust them off every day,** or as often as you can.
- The projection team at Playa Alchemist keeps its projectors in expensive
  air-conditioned enclosures that are never opened on playa.
- The cheaper version: **an enclosure with a window for the lens, plus fans.**

## Content ideas

- **Missing-child panel:** show the missing-child outline during the day, then projection
  map it at night. For example, make the child cry, or animate only the lips.
- **AI video:** one option is to make the projected effects fully as AI-generated video.
- **"MILK" lettering:** put a stroke (outline) on the text instead of coloring it a
  different color.
- **Conflict:** `design-decisions.md` says **Decided: no "lost child" panel** on the
  carton. `budget.md` already mentions "missing kid" visuals for night projection only.
  A missing-child outline painted on during the day would reverse that decision, so
  Allison and Quentin need to decide. It is not changed here.

## Rough costs (Tyler's estimate)

| Item | Tyler's estimate | Notes |
|---|---|---|
| Lights and cords | ~$500 | Govee Outdoor Flood Lights 2 ($179.99 per 6 pack) plus cabling. |
| Two projectors | ~$3,000 | Less if used ones turn up on Facebook Marketplace. |
| Resolume Arena | ~$600, or ~$300 on sale | The site lists €799, about $895. About $450 at 50% off. See above. |
| Computer to run Resolume | TBD | Not priced. |
| Projector enclosures (window + fans) | TBD | Not priced. |
| Solar power system | TBD | Decided: solar. Not priced. Size it from the real load (see Power). |
| Dusk-to-dawn timer(s) | ~$12 each | UltraPro 86940-T1. |

Roughly $4,000 to $4,400 for lights, projectors, and Arena, depending on the Resolume
price. That leaves out the computer, enclosures, and power. These are estimates
from a phone call, not quotes. `budget.md` carries them with that label.

## Next steps

1. **Build a tiny prototype.** Use a small carton mock-up, one wash light with a shield,
   and one projector mapped with Resolume (the free trial works for testing; its output
   is watermarked).
2. **Buy Resolume Arena in the Black Friday sale** (Fri Nov 27, 2026) if the
   prototype goes well.
3. Look at short-throw projectors in the 5,000 to 7,000 lumen range, and check
   Facebook Marketplace for used ones.
4. Work out how many Govee flood light sets cover the base.
5. Add up the nightly load (lights + projectors + computer) to size the solar system.
6. Decide whether to add a daytime missing-child outline (see
   `open-questions.md`).
