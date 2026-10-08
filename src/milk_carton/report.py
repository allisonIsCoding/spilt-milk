"""Plain-text numbers and checks for a configuration."""

from __future__ import annotations

from .config import Config
from .geometry import Carton
from .stairs import Layout, layout as make_layout, sweep


def summary(cfg: Config, carton: Carton | None = None, lay: Layout | None = None) -> str:
    carton = carton or Carton(cfg)
    lay = lay or make_layout(cfg, carton)
    sx, sz = carton.spout_point()
    xl, xr = carton.v_range_at(0)
    lines = [
        "# Milk carton: numbers and checks",
        "",
        "## Carton",
        f"- Tilt {cfg.tilt_deg:.0f} deg from vertical; the climbing surface slopes {carton.floor_slope_deg:.0f} deg "
        f"and the old bottom panel {carton.panel_slope_deg:.0f} deg from horizontal.",
        f"- {cfg.height_ft:.0f} ft tall, {cfg.width_ft:.0f} x {cfg.width_ft:.0f} ft footprint, "
        f"body {cfg.body_ft:.0f} ft, roof {cfg.roof_ft:.0f} ft, fin {cfg.fin_ft:.0f} ft.",
        f"- Highest point {carton.top_height():.1f} ft above grade; the base corner is sunk {cfg.sink_ft:.1f} ft.",
        f"- At grade the V-shaped interior is {xr - xl:.1f} ft wide "
        f"({xl:.1f} to {xr:.1f} ft from the base corner).",
        "",
        "## Spout and slide",
        f"- Spout {sz:.1f} ft above grade and {sx:.1f} ft out from the base corner.",
        f"- Slide drops {sz - cfg.slide_half_width_ft:.1f} ft over about {carton.slide_length_ft():.0f} ft of travel; "
        f"steepest section {carton.slide_max_slope_deg():.0f} deg.",
        "",
        "## Stairs",
        f"- {cfg.stair_width_ft:.1f} ft clear width, {len(lay.flights)} flights, landing every "
        f"{cfg.landing_interval_ft:.1f} ft of climb, flight skew {cfg.flight_skew_ft:.1f} ft.",
        f"- Pitch per flight: " + ", ".join(f"{f.pitch_deg:.0f}" for f in lay.flights) + " deg.",
        f"- Longest possible fall: one flight, {lay.max_fall_ft:.1f} ft.",
        f"- Room for the launch deck: {lay.deck_room_ft:.1f} ft along the carton.",
        f"- Smallest gap between stairs and carton surfaces: {lay.min_clearance_ft:.2f} ft.",
        "",
        "## Checks",
    ]
    if not lay.issues:
        lines.append("- All checks pass.")
    for level, msg in lay.issues:
        lines.append(f"- {level.upper()}: {msg}")
    return "\n".join(lines) + "\n"


def sweep_table(cfg: Config, **kwargs) -> str:
    rows = sweep(cfg, **kwargs)
    out = ["| Width (ft) | Landing every (ft) | Flights | Worst pitch | Longest fall | Result |",
           "|---|---|---|---|---|---|"]
    for r in rows:
        result = "ok" if r["ok"] else "fails: " + r["first_problem"]
        out.append(f"| {r['width']:.1f} | {r['interval']:.0f} | {r['flights']} | {r['worst_pitch']:.0f}° | "
                   f"{r['max_fall']:.0f} ft | {result} |")
    return "\n".join(out) + "\n"
