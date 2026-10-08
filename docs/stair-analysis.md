# Why the stairs look the way they do

Writing the schematic as code made the geometry checkable, and it turned up several things
that the earlier hand-drawn versions (and some of my earlier answers) got wrong. This page
is the corrected picture.

## The space

At a 50 degree tilt the inside of the carton is a V-shaped trough, 16 ft deep:

- The surface you climb slopes **40 degrees**. A normal stair is 30 to 35 degrees, and
  codes top out near 38.
- The old bottom panel slopes **50 degrees** the other way.
- Anything built inside has to stay above both surfaces, so the stairs are a freestanding
  switchback: flights cross the carton's depth and each turn steps forward along its
  length.
- At grade the V is only **5.7 ft wide**. With a half foot of clearance on each side, only
  about 4.7 ft is usable where the first flight starts.

## Two limits that decide everything

1. **The first flight starts at ground level inside a 5.7 ft gap.** Stairs wider than about
   4.7 ft cannot start there.
2. **Pitch is set by the depth, not just the rise.** A landing must be as deep as the stairs
   are wide, and a landing sits at each end of a flight. So a middle flight only has
   `16 - 2 x width` feet to climb its 4 or 5 ft:
   4.0 ft wide leaves 8 ft of run, 4.5 ft leaves 7 ft, and 5.5 ft leaves only 5 ft of run
   (45 degrees for a 5 ft rise).

## Diagonal flights do not fit

Tilting the flights (skew) lengthens them and lowers their pitch. But every foot a flight
advances along the carton raises the 40 degree floor under it by 0.84 ft. Straight-across
flights already advance about 4.5 ft per 4 ft of climb, which is close to the limit
(1.19 ft along per foot up). Any real skew pushes the stairs into the floor. The generator
fails 1 ft of skew on clearance (`--set flight_skew_ft=1`).

So "diagonal" stairs in practice means the flights run straight across the carton's width,
stacked along its length, with landings at alternating sides. That is what the plan shows.

## Sweep (default carton, 50 degree tilt)

| Width (ft) | Landing every (ft) | Flights | Worst pitch | Longest fall | Result |
|---|---|---|---|---|---|
| 4.0 | 3 | 7 | 21° | 3 ft | fails: Flight 2 comes within 0.43 ft of the carton surface (need 0.5). |
| 4.0 | 4 | 5 | 27° | 4 ft | ok |
| 4.0 | 5 | 4 | 32° | 5 ft | ok |
| 4.5 | 3 | 7 | 23° | 3 ft | fails: Flight 2 comes within -0.20 ft of the carton surface (need 0.5). |
| 4.5 | 4 | 5 | 30° | 4 ft | ok |
| 4.5 | 5 | 4 | 36° | 5 ft | ok |
| 5.0 | 3 | 7 | 27° | 3 ft | fails: At grade the V is only 5.7 ft wide and 4.7 ft once 0.5 ft of clearance is kept; a 5.0 ft flight does not fit. |
| 5.0 | 4 | 5 | 34° | 4 ft | fails: At grade the V is only 5.7 ft wide and 4.7 ft once 0.5 ft of clearance is kept; a 5.0 ft flight does not fit. |
| 5.0 | 5 | 4 | 40° | 5 ft | fails: At grade the V is only 5.7 ft wide and 4.7 ft once 0.5 ft of clearance is kept; a 5.0 ft flight does not fit. |
| 5.5 | 3 | 7 | 31° | 3 ft | fails: At grade the V is only 5.7 ft wide and 4.7 ft once 0.5 ft of clearance is kept; a 5.5 ft flight does not fit. |
| 5.5 | 4 | 5 | 39° | 4 ft | fails: At grade the V is only 5.7 ft wide and 4.7 ft once 0.5 ft of clearance is kept; a 5.5 ft flight does not fit. |
| 5.5 | 5 | 4 | 45° | 5 ft | fails: At grade the V is only 5.7 ft wide and 4.7 ft once 0.5 ft of clearance is kept; a 5.5 ft flight does not fit. |
| 6.0 | 3 | 7 | 37° | 3 ft | fails: At grade the V is only 5.7 ft wide and 4.7 ft once 0.5 ft of clearance is kept; a 6.0 ft flight does not fit. |
| 6.0 | 4 | 5 | 45° | 4 ft | fails: At grade the V is only 5.7 ft wide and 4.7 ft once 0.5 ft of clearance is kept; a 6.0 ft flight does not fit. |
| 6.0 | 5 | 4 | 51° | 5 ft | fails: At grade the V is only 5.7 ft wide and 4.7 ft once 0.5 ft of clearance is kept; a 6.0 ft flight does not fit. |
"Worst pitch" is the steepest flight. Comfort limit is 35 degrees and the hard limit is 38.

## What the numbers support

- **4.5 ft wide, landing every 4 ft** (the default): 5 flights, pitches 19, 30, 30, 30, 27
  degrees, longest fall 4 ft, 13.8 ft left for the launch deck. Passes every check.
- **4.0 ft wide, landing every 5 ft**: 4 flights, worst pitch 32 degrees, longest fall 5 ft.
  Fewer flights, but a longer fall and a narrower stair.
- **5.0 and 5.5 ft wide**: do not fit at grade, and the pitch gets too steep anyway.
- Landings every 3 ft fail on clearance: the stack moves along the carton faster than the floor
  under it climbs, so the stairs run into the floor.

## Levers if you want it wider or gentler

- **A deeper carton.** This makes the stairs gentler, not wider. At 18 ft deep a 4.5 ft stair drops to
  24 degrees, but 5.0 ft still fails because the V at grade does not change. The carton also gets about
  12 percent less true to the real proportions.
- **Start the first flight above grade.** A raised door and a short outside stair lets the
  first flight start where the V is wider. This changes the entry.
- **Sink the carton deeper.** More sink widens the V at grade, but lowers the spout and
  changes the slide. In my tests (up to 4 ft of sink) 5.5 ft still failed.
- **A different tilt.** 45 degrees makes both inner surfaces 45 degrees and fits 4.0 ft stairs
  with 6 flights. 55 degrees fails on the top landing.

Run any of these with `--set`, for example
`PYTHONPATH=src python3 -m milk_carton --set width_ft=18 --out /tmp/wide`.

## Corrections to earlier answers

- Earlier I said **5.5 ft is the maximum width that fits**, and that **pitch barely changes
  with width**. Both were wrong. The numbers above replace them.
- Earlier I said the entry could be at the low corner, reached from outside under the
  overhang. That does not work: the wall slopes at 40 degrees. The entry is a door in the
  front face.
- Earlier plan drawings let flights overlap landings at different heights. The code now
  rejects layouts where two surfaces overlap in plan with less than 6.7 ft of headroom.
