# Image prompts (for Gemini and other generators)

Current design: the upright carton, baby blue and white, with the slide coming out of a
tear in the spout-end wall. Numbers come from `config/default.json`
(see `outputs/report.md`).

How to use: start a new chat, paste the full prompt, and attach `outputs/spout.png` and
`outputs/upright_elevation.png` as shape references (say "use these drawings for the shape
and proportions only, not the colours"). Then change one thing at a time in follow-ups.

## Full prompt

> Create a photorealistic wide shot of a monumental art installation at Burning Man: a
> giant classic gable-top milk carton, about 40 feet tall, standing upright on the flat,
> pale, cracked desert playa. It is built entirely from plywood and lumber and fully
> painted. Subtle panel seams and a little dust and sun-fading are visible, but there is
> no exposed scaffolding or framing.
>
> SHAPE AND PROPORTIONS: It has the proportions of a one-gallon carton. The footprint is a
> rectangle about 25 feet long by 19 feet wide. The straight vertical walls rise about
> 31 feet. Above them sits a short gable roof, two sloping panels meeting at a ridge that
> runs along the long direction, about 7 feet tall. A thin, flat, vertical sealed fin about
> 2 feet tall runs along the top of the ridge. The roof and fin together are only the top
> quarter of the carton; the walls are most of its height.
>
> THE SPOUT: The spout is on one of the two narrow (19-foot) ends, at the top, and it is
> pulled open exactly like a real carton. The triangular end of the roof has swung outward,
> hinged at the top of the end wall, forming a pointed V-shaped pouring spout. Its tip sticks
> out about 5 feet past the end wall and sits slightly higher than the fin. The roof corners
> next to the spout are bent along diagonal creases, and the end of the fin is lifted up
> toward the spout tip. The whole diamond-shaped top of the spout is open, facing up at the
> sky, dark inside.
>
> COLOURS: Retro baby-blue-and-white milk carton. The walls are crisp white with soft
> baby blue (pale sky blue) panels and bands; the roof panels and fin are baby blue. The long side carries large, simple,
> retro lettering that says "MILK", drawn as a baby blue
> outline only (hollow letters, white inside, not filled in). No brand names, logos, or other text.
>
> THE SLIDE: A bit under halfway up the narrow spout-end wall (around 9 feet up),
> centered on that wall, the wall is torn open in a jagged rip, as if the carton has burst. A thick,
> glossy white stream of milk gushes out of the tear and becomes a smooth sculpted wooden
> slide painted milk-white. It leaves the tear nearly level, curves over, slopes down at a
> gentle playground angle, and eases out about 23 feet from the carton into a wide, low,
> splashy puddle of milk on the ground. A few slim white posts support the slide. People
> are sliding down it and landing in the puddle.
>
> PEOPLE AND SCALE: A doorway at ground level on the long side near one corner, with people
> walking in. A few people in colourful Burning Man costumes stand around the base for scale
> (an adult is about one-seventh of the wall height).
>
> SETTING AND CAMERA: Black Rock City at golden hour, warm low sunlight, long shadows, a
> little dust in the air, distant mountains and a few far-off art pieces and art cars. Camera
> at eye level, a three-quarter view from the front corner so both the long side and the
> spout end with the slide are visible.
>
> LEAVE OUT: a tipped-over or tilted carton; a slide that wraps around the carton; a
> plastic jug or glass bottle; a screw cap; any opening other than the open spout on top and
> the one tear with the slide; exposed scaffolding; brand logos; extra text.

## Short version

> Photorealistic: a 40 ft tall wooden milk carton art installation standing upright on the
> Burning Man playa at golden hour. One-gallon proportions (25 x 19 ft footprint, tall walls,
> short gable roof with a thin fin). Retro baby-blue-and-white carton paint with big outlined (hollow) "MILK"
> lettering, no brands. The spout on one narrow end is pulled open like a real carton, its
> tip just above the fin, the diamond-shaped top open to the sky. About 9 ft up that end
> wall, centered, a jagged tear gushes glossy white milk that becomes a sculpted white wooden slide
> curving down into a wide milk puddle, with people sliding. People in costumes for scale.
> No tilted carton, no wrap-around slide, no logos, no scaffolding.

## Follow-up edits that tend to help

- "Make the walls taller and the roof shorter: the roof and fin are only the top quarter."
- "The spout tip must stick out past the end wall and rise just above the fin."
- "Only one tear, centered on the narrow end with the spout, about 9 ft up."
- "Keep the slide straight out from the tear; it does not go around the carton."
