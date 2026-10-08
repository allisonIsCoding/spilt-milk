"""Top-down plan of the stairs inside the carton.

Looking straight down: X runs left to right along the carton (the spout end is
on the right), y runs front (bottom of the drawing) to back (top).
"""

from __future__ import annotations

from .config import Config
from .geometry import Carton
from .stairs import Layout, layout as make_layout
from .svgdoc import SVG

KP = 16.0                  # pixels per foot
OXP, BASE = 228.0, 330.0   # pixel x of X = 0, pixel y of the front face (y = 0)
W_PX, H_PX = 940, 570


def PP(X: float, y: float) -> tuple[float, float]:
    return (OXP + KP * X, BASE - KP * y)


def render(cfg: Config, carton: Carton | None = None, lay: Layout | None = None) -> str:
    carton = carton or Carton(cfg)
    lay = lay or make_layout(cfg, carton)
    W = cfg.width_ft
    svg = SVG(W_PX, H_PX, "Plan of the zigzag stairs",
              "Top-down view of the switchback stairs crossing the carton's depth, with landings at each turn.")

    shell = carton.to_world_poly(carton.body_local()) + carton.to_world_poly(carton.roof_local())
    xmin = min(p[0] for p in shell)
    xmax = max(p[0] for p in shell)
    a, b = PP(xmin, W), PP(xmax, 0)
    svg.rect(a[0], a[1], b[0] - a[0], b[1] - a[1], "shell")

    # where the two sloping walls meet grade
    xl, xr = carton.panel_cross_grade_X(), carton.floor_cross_grade_X()
    v0, v1 = PP(xl, W), PP(xr, 0)
    svg.rect(v0[0], v0[1], v1[0] - v0[0], v1[1] - v0[1], "ground", 'fill-opacity="0.6" stroke="none"')
    for X in (xl, xr):
        svg.line(PP(X, 0), PP(X, W + 0.8), "leader")
    svg.text(PP(xl, 0)[0] - 6, PP(0, W + 1.4)[1], "bottom panel meets grade", "xs", "end")
    svg.text(PP(xr, 0)[0] + 6, PP(0, W + 1.4)[1], "climbing floor meets grade", "xs")

    for f in lay.flights:
        svg.polygon([PP(*p) for p in f.poly], "flight")
    for ln in lay.landings:
        x0, x1, y0, y1 = ln.rect
        p0, p1 = PP(x0, y1), PP(x1, y0)
        svg.rect(p0[0], p0[1], p1[0] - p0[0], p1[1] - p0[1], "landing")
        label = "Launch deck" if ln.is_launch else "Landing"
        cx, cy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        svg.text(cx, cy - 2, label, "h", "middle")
        svg.text(cx, cy + 14, f"{ln.z:.0f} ft up", "xs", "middle")
    for x0, x1, y0, y1 in lay.deck_extra:
        p0, p1 = PP(x0, y1), PP(x1, y0)
        svg.rect(p0[0], p0[1], p1[0] - p0[0], p1[1] - p0[1], "landing")

    for f in lay.flights:
        poly = f.poly
        s = ((poly[0][0] + poly[1][0]) / 2, poly[0][1])
        e = ((poly[2][0] + poly[3][0]) / 2, poly[2][1])
        svg.line(PP(*s), PP(*e), "dim", 'marker-start="url(#arrow)" marker-end="url(#arrow)"')
        mid = PP((s[0] + e[0]) / 2, (s[1] + e[1]) / 2)
        svg.text(mid[0] + 8, mid[1] - 4, f"{f.pitch_deg:.0f}°", "xs")

    # entry door in the front face
    f1 = lay.flights[0]
    ex = PP(f1.xs + f1.extent_ft / 2, 0)
    svg.line((ex[0], ex[1] + 40), (ex[0], ex[1] + 3), "dim", 'marker-end="url(#arrow)"')
    svg.text(ex[0], ex[1] + 56, "Entry door (front face)", "s", "middle")

    # spout, centered on the ridge
    sx, _ = carton.spout_point()
    c = PP(sx, W / 2)
    svg.polygon([(c[0] - 2, c[1] - 12), (c[0] - 2, c[1] + 12), (c[0] + 14, c[1])], "mouth")
    svg.text(c[0] - 8, c[1] - 22, "Spout and slide", "s")

    # depth dimension
    dx = PP(xmax, 0)[0] + 60
    svg.line((dx, PP(0, 0)[1]), (dx, PP(0, W)[1]), "dim", 'marker-start="url(#arrow)" marker-end="url(#arrow)"')
    svg.text(dx + 8, (PP(0, 0)[1] + PP(0, W)[1]) / 2 + 4, f"{W:.0f} ft deep", "h")

    # legend and findings
    y = BASE + 95
    svg.rect(60, y, 16, 16, "flight")
    svg.text(84, y + 13, f"Flight, {cfg.stair_width_ft:.1f} ft clear, two-way (number = pitch)", "s")
    svg.rect(420, y, 16, 16, "landing")
    svg.text(444, y + 13, f"Landing, {cfg.landing_depth:.1f} ft deep, railed", "s")
    svg.text(60, y + 42, f"{len(lay.flights)} flights, a landing every {cfg.landing_interval_ft:.0f} ft of climb, "
                         f"longest fall {lay.max_fall_ft:.0f} ft, launch deck {lay.launch_z:.1f} ft up.", "s")
    yy = y + 64
    if not lay.issues:
        svg.text(60, yy, "All checks pass.", "s")
    for level, msg in lay.issues[:4]:
        color = "#a32d2d" if level == "fail" else "#854f0b"
        svg.add(f'<text x="60" y="{yy}" fill="{color}" style="fill:{color}">{"FAIL" if level == "fail" else "WARN"}: {_esc(msg)}</text>')
        yy += 18
    return svg.render()


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
