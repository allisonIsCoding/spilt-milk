"""Side elevation: the tipped carton in section, with stairs, slide and ground."""

from __future__ import annotations

import math

from .config import Config
from .geometry import PUDDLE, Carton
from .stairs import Layout, layout as make_layout
from .svgdoc import SVG, fmt

K = 11.0          # pixels per foot
OX, GY = 240.0, 540.0
W_PX, H_PX = 1000, 650
SLAB = 0.35       # landing thickness, ft


def P(X: float, z: float) -> tuple[float, float]:
    return (OX + K * X, GY - K * z)


def render(cfg: Config, carton: Carton | None = None, lay: Layout | None = None) -> str:
    carton = carton or Carton(cfg)
    lay = lay or make_layout(cfg, carton)
    svg = SVG(W_PX, H_PX, "Side elevation of the tipped milk carton",
              f"Carton tipped {cfg.tilt_deg:.0f} degrees with railed zigzag stairs inside and a spill-shaped slide.")

    # ---- shell -------------------------------------------------------------
    svg.polygon([P(*p) for p in carton.to_world_poly(carton.body_local())], "shell")
    svg.polygon([P(*p) for p in carton.to_world_poly(carton.roof_local())], "shell")
    r0, r1 = carton.ridge_line_local()
    svg.line(P(*carton.to_world(*r0)), P(*carton.to_world(*r1)), "dim", 'stroke="#185fa5" stroke-width="0.8"')
    svg.polygon([P(*p) for p in carton.mouth_world()], "mouth")

    # ---- stairs ------------------------------------------------------------
    for f in lay.flights:
        lo_l, lo_r = f.xs, f.xs + f.extent_ft
        hi_l = f.xs + cfg.flight_skew_ft
        hi_r = hi_l + f.extent_ft
        svg.polygon([P(lo_l, f.z0), P(lo_r, f.z0), P(hi_r, f.z1), P(hi_l, f.z1)], "flight")
    for ln in lay.landings:
        x0, x1, _, _ = ln.rect
        top = P(x0, ln.z)
        svg.rect(top[0], top[1], K * (x1 - x0), K * SLAB, "landing")
        for X in (x0, x1):
            base = _support_z(carton, X)
            if ln.z - SLAB - base > 0.2:
                a, b = P(X, ln.z - SLAB), P(X, base)
                svg.line(a, b, "post")
        # guard rail around the landing
        a, b = P(x0, ln.z + cfg.rail_height_ft), P(x1, ln.z + cfg.rail_height_ft)
        svg.line(a, b, "rail")
        for X in (x0, x1):
            svg.line(P(X, ln.z), P(X, ln.z + cfg.rail_height_ft), "rail")

    f1 = lay.flights[0]
    d0, d1 = P(f1.xs, cfg.door_height_ft), P(f1.xs + f1.extent_ft, 0)
    svg.rect(d0[0], d0[1], d1[0] - d0[0], d1[1] - d0[1], "door")

    # ---- ground ------------------------------------------------------------
    svg.rect(20, GY, W_PX - 40, 70, "ground")
    fx0, fx1, fdepth = -9.5, 12.5, 5.3
    a = P(fx0, 0)
    svg.rect(a[0], GY, K * (fx1 - fx0), K * fdepth, "footing")
    svg.text(P(fx1, 0)[0] + 14, GY + 38, "Footing below grade", "s")

    # ---- slide -------------------------------------------------------------
    sx, sz = carton.slide_end()
    for dx in cfg.slide_support_fracs:
        X = carton.spout_point()[0] + dx * cfg.slide_run_ft
        z = carton.slide_z_at(X) - cfg.slide_half_width_ft
        svg.line(P(X, z), P(X, 0), "post", 'stroke-dasharray="4 3"')
    p0 = PUDDLE[0]
    d = f"M{_xy(sx + p0[0], p0[1])}"
    for c1, c2, p in PUDDLE[1:]:
        d += f" C{_xy(sx + c1[0], c1[1])} {_xy(sx + c2[0], c2[1])} {_xy(sx + p[0], p[1])}"
    svg.path(d + " Z", "puddle")
    segs = carton.slide_path()
    d = f"M{_xy(*segs[0][0])}"
    for _, c1, c2, p in segs:
        d += f" C{_xy(*c1)} {_xy(*c2)} {_xy(*p)}"
    wpx = 2 * cfg.slide_half_width_ft * K
    svg.path(d, "milk-edge", f'stroke-width="{fmt(wpx + 2)}"')
    svg.path(d, "milk", f'stroke-width="{fmt(wpx)}"')

    # ---- 40 ft dimension and tilt -----------------------------------------
    u0 = -cfg.width_ft - 2.5
    b, t = P(*carton.to_world(u0, 0)), P(*carton.to_world(u0, cfg.height_ft))
    svg.line(b, t, "dim", 'marker-start="url(#arrow)" marker-end="url(#arrow)"')
    svg.text(t[0] - 10, t[1] - 4, f"{cfg.height_ft:.0f} ft", "h", "end")
    r = 6.5 * K
    ang = math.radians(cfg.tilt_deg)
    svg.line(b, (b[0], b[1] - r - 22), "dim", 'stroke-dasharray="4 3"')
    svg.path(f"M{fmt(b[0])} {fmt(b[1] - r)} A{fmt(r)} {fmt(r)} 0 0 1 "
             f"{fmt(b[0] + r * math.sin(ang))} {fmt(b[1] - r * math.cos(ang))}", "dim")
    svg.text(b[0] - 8, b[1] - r - 6, f"Tilt {cfg.tilt_deg:.0f}°", "s", "end")

    # ---- person for scale --------------------------------------------------
    Xp = (8.5 + cfg.sink_ft) * math.tan(carton.t) + 1.5
    hx, hy = P(Xp, 0)
    ph = cfg.person_ft * K
    svg.circle((hx, hy - ph + 0.45 * K), 0.45 * K, "person")
    svg.line((hx, hy - ph + 0.9 * K), (hx, hy - 0.45 * ph), "person")
    svg.line((hx, hy - 0.45 * ph), (hx - 0.9 * K, hy), "person")
    svg.line((hx, hy - 0.45 * ph), (hx + 0.9 * K, hy), "person")
    svg.line((hx, hy - 0.8 * ph), (hx - 1.1 * K, hy - 0.55 * ph), "person")
    svg.line((hx, hy - 0.8 * ph), (hx + 1.1 * K, hy - 0.55 * ph), "person")
    svg.text(hx + 1.4 * K, hy - 0.4 * ph, f"{cfg.person_ft:.0f} ft person", "s")

    # ---- labels ------------------------------------------------------------
    tip = P(*carton.tip_world())
    svg.line((tip[0] + 4, tip[1] - 4), (tip[0] + 24, tip[1] - 36), "leader")
    svg.text(tip[0] + 28, tip[1] - 42, "Pull-open spout", "h")
    svg.text(tip[0] + 28, tip[1] - 24, "In line with ridge", "s")

    poly = carton.slide_polyline(60)
    mid = P(*poly[int(len(poly) * 0.42)])
    svg.line((mid[0] + 14, mid[1] - 2), (mid[0] + 32, mid[1] - 10), "leader")
    svg.text(mid[0] + 36, mid[1] - 6, "Spill slide", "s")
    svg.text(P(sx, 0)[0] - 40, GY - 52, "Puddle landing", "s")
    first_post = P(carton.spout_point()[0] + cfg.slide_support_fracs[0] * cfg.slide_run_ft, 0)
    svg.text(first_post[0] - 30, GY + 22, "Slide supports", "s")

    target_landing = lay.landings[min(2, len(lay.landings) - 1)]
    lx = P((target_landing.rect[0] + target_landing.rect[1]) / 2, target_landing.z)
    svg.text(24, 96, "Railed zigzag stairs", "h")
    svg.text(24, 114, f"{cfg.stair_width_ft:.1f} ft clear, landing every {cfg.landing_interval_ft:.0f} ft", "s")
    svg.line((150, 122), (lx[0] - 6, lx[1] - 4), "leader")

    door_mid = P(f1.xs, cfg.door_height_ft / 2)
    svg.text(24, 500, "Entry door", "h")
    svg.text(24, 517, "in the front face", "s")
    svg.line((112, 508), (door_mid[0] - 2, door_mid[1]), "leader")

    # ---- caption -----------------------------------------------------------
    spx, spz = carton.spout_point()
    caption = (f"Spout {spz:.0f} ft above grade, {spx:.0f} ft out from the base corner  |  "
               f"slide drop {spz - cfg.slide_half_width_ft:.0f} ft, steepest {carton.slide_max_slope_deg():.0f} deg  |  "
               f"stairs: {len(lay.flights)} flights, worst pitch {lay.max_pitch_deg:.0f} deg, longest fall {lay.max_fall_ft:.0f} ft")
    svg.text(24, H_PX - 18, caption, "xs")
    return svg.render()


def _support_z(carton: Carton, X: float) -> float:
    z = carton.floor_z(X) if X >= 0 else carton.panel_z(X)
    return z if z is not None else -carton.sink


def _xy(X: float, z: float) -> str:
    x, y = P(X, z)
    return f"{fmt(x)} {fmt(y)}"
