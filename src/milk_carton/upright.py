"""Upright carton: standing on its base, stairs spiralling up the inside walls.

Coordinates: X along the front face (0..W, the spout end is X = W), y from the
front face (0) to the back face (W), z up from grade.

The ridge runs along X. The two roof panels slope up from the front and back
eaves (body_ft) to the ridge (body_ft + roof_ft); the fin sits on top. The
classic pull-open spout is the top of the gable end at X = W, pulled out.

Stairs: a spiral against the four walls, a landing in each corner (and partway
along the long walls), up to the "eave deck", a full floor just below the roof
that doubles as a lookout.

The slide: milk pours out of a tear in the spout-end wall at the landing there
and runs straight out into a puddle. The spout at the top is open for the look.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .config import Config
from .svgdoc import SVG

Point = tuple[float, float]


# ---- model --------------------------------------------------------------------

@dataclass
class Upright:
    cfg: Config
    issues: list[tuple[str, str]] = field(default_factory=list)

    def __post_init__(self):
        c = self.cfg
        self.W = c.width_ft                               # across the gable end (y)
        self.L = c.length_ft or c.width_ft                # along the ridge (X); the spout is at X = L
        self.Hb, self.R, self.H = c.body_ft, c.roof_ft, c.height_ft
        self.ridge = self.Hb + self.R
        self.inner_x = self.L - 2 * c.wall_ft
        self.inner_y = self.W - 2 * c.wall_ft
        self.inner = self.inner_x
        self.w = c.stair_width_ft
        self.well_x = self.inner_x - 2 * self.w
        self.well_y = self.inner_y - 2 * self.w
        self.deck_z = c.eave_deck_ft
        self._spiral()
        # Opened spout (side view): the end of the gable swings out on a hinge at the top of the
        # end wall; its front crease runs up to the tip, which ends up above the fin. The roof
        # corner bends along a crease from the hinge to where the fin starts lifting, and the
        # side flap along a crease from the hinge to the lifted fin.
        self.hinge = (self.L, self.Hb)
        self.tip_X = self.L + c.spout_tip_out_ft
        self.tip_z = self.H + c.spout_tip_above_ft
        self.crease_top = (self.L - c.spout_crease_back_ft, self.tip_z)
        self.lift_start = (self.L - c.fin_lift_back_ft, self.H)
        self._check()

    # ---- spiral stairs ------------------------------------------------------------
    def _spiral(self):
        """Flights against the four walls, a landing in each corner, and a mid-wall landing
        on any wall too long for one flight. Every flight has the same pitch."""
        c, w, a = self.cfg, self.w, self.cfg.wall_ft
        bx, by = self.L - a, self.W - a
        corners = [(a, a + w, a, a + w), (bx - w, bx, a, a + w), (bx - w, bx, by - w, by), (a, a + w, by - w, by)]
        # walls in spiral order: front (+X), spout end (+y), back (-X), far end (-y)
        segs = []    # ("flight", rect, run, axis) or ("landing", rect)
        for k in range(c.spiral_flights * 2):          # more than enough walls; trimmed below
            i = k % 4
            r0, r1 = corners[i], corners[(i + 1) % 4]
            along_x = i % 2 == 0
            if along_x:
                lo, hi = (r0[1], r1[0]) if i == 0 else (r1[1], r0[0])
                y0, y1 = r0[2], r0[3]
                span = hi - lo
                pieces = 2 if span > c.max_flight_run_ft else 1
                run = (span - (pieces - 1) * w) / pieces
                xs = lo
                order = []
                for p_ in range(pieces):
                    order.append(("flight", (xs, xs + run, y0, y1), run))
                    xs += run
                    if p_ < pieces - 1:
                        order.append(("landing", (xs, xs + w, y0, y1)))
                        xs += w
                if i == 2:
                    order = order[::-1]
            else:
                lo, hi = (r0[3], r1[2]) if i == 1 else (r1[3], r0[2])
                x0, x1 = r0[0], r0[1]
                span = hi - lo
                pieces = 2 if span > c.max_flight_run_ft else 1
                run = (span - (pieces - 1) * w) / pieces
                ys = lo
                order = []
                for p_ in range(pieces):
                    order.append(("flight", (x0, x1, ys, ys + run), run))
                    ys += run
                    if p_ < pieces - 1:
                        order.append(("landing", (x0, x1, ys, ys + w)))
                        ys += w
                if i == 3:
                    order = order[::-1]
            segs += order + [("landing", r1)]
        # keep exactly spiral_flights flights
        kept, nf = [], 0
        for sgm in segs:
            if sgm[0] == "flight":
                if nf == c.spiral_flights:
                    break
                nf += 1
            kept.append(sgm)
        total_run = sum(sg[2] for sg in kept if sg[0] == "flight")
        t = self.deck_z / total_run
        self.pitch = math.degrees(math.atan(t))
        z = 0.0
        self.flights, self.lands = [], [(0.0, corners[0], "entry")]
        for sg in kept:
            if sg[0] == "flight":
                r, run = sg[1], sg[2]
                self.flights.append((z, z + run * t, r, run))
                z += run * t
            else:
                self.lands.append((z, sg[1], "landing"))
        self.n = len(self.flights)
        self.run = max(f[3] for f in self.flights)
        self.max_rise = max(f[1] - f[0] for f in self.flights)
        self.lap_rise = (2 * (self.inner_x + self.inner_y) - 8 * w) * t

    # roof underside height at distance y from the front face
    def roof_z(self, y: float) -> float:
        d = min(y, self.W - y)
        return self.Hb + max(0.0, d) * self.R / (self.W / 2)

    def _check(self):
        c, add = self.cfg, self.issues.append
        if min(f[3] for f in self.flights) < 2.0:
            add(("fail", f"{self.w:.1f} ft stairs leave too little run along the walls."))
        if self.pitch > c.max_pitch_deg:
            add(("fail", f"Wall flights are {self.pitch:.0f} deg (max {c.max_pitch_deg:.0f}); add flights."))
        elif self.pitch > c.comfort_pitch_deg:
            add(("warn", f"Wall flights are {self.pitch:.0f} deg (comfort limit {c.comfort_pitch_deg:.0f})."))
        if self.lap_rise < c.headroom_ft:
            add(("fail", f"One lap climbs only {self.lap_rise:.1f} ft, less than the {c.headroom_ft:.1f} ft headroom."))
        # wall flights and corner landings sit against the front and back walls, under the eaves
        wall_head = self.roof_z(c.wall_ft) - self.deck_z
        if wall_head < c.headroom_ft:
            add(("fail", f"The eave deck at {self.deck_z:.1f} ft has only {wall_head:.1f} ft of headroom at the "
                         f"front and back walls (need {c.headroom_ft:.1f})."))
        # the outlet is a landing against the spout-end wall
        out = self.outlet_landing()
        if out is None or abs(out[0] - c.side_outlet_ft) > 0.3:
            near = ", ".join(f"{z:.1f}" for z, r, _ in self.lands if r[1] >= self.L - c.wall_ft - 1e-6 and z > 0)
            add(("fail", f"The slide outlet at {c.side_outlet_ft:g} ft is not at a landing on the spout-end wall "
                         f"(landings there: {near} ft)."))

    def outlet_landing(self):
        """The landing against the spout-end wall closest to the outlet height."""
        c = self.cfg
        cands = [(z, r, k) for z, r, k in self.lands if r[1] >= self.L - c.wall_ft - 1e-6 and z > 0]
        return min(cands, key=lambda t: abs(t[0] - c.side_outlet_ft)) if cands else None

    # ---- slide: side outlet ----------------------------------------------------
    def side_slide(self, n: int = 120) -> list[Point]:
        """(X, z) centreline for a slide leaving the spout-end wall at outlet height."""
        c = self.cfg
        x0, z0 = self.L, c.side_outlet_ft
        drop = z0 - 0.6
        # gentle pour: level, roll over, straight at the target grade, ease out
        g = math.tan(math.radians(c.side_slide_deg))
        run = drop / g * 1.25
        p0, p1, p2, p3 = (x0, z0), (x0 + 0.3 * run, z0), (x0 + 0.55 * run, 0.6), (x0 + run, 0.6)
        out = []
        for i in range(n + 1):
            t = i / n
            a, b, cc, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
            out.append((a * p0[0] + b * p1[0] + cc * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + cc * p2[1] + d * p3[1]))
        self.side_run = run
        self.side_max_deg = max(math.degrees(math.atan2(za - zb, xb - xa))
                                for (xa, za), (xb, zb) in zip(out, out[1:]) if xb > xa)
        return out


# ---- drawings -------------------------------------------------------------------

K = 15.0


def _elev_frame(u: Upright, svg: SVG, P):
    c, W = u.cfg, u.L
    # ground
    svg.rect(10, P(0, 0)[1], svg.w - 20, 60, "ground")
    # body, roof panel, fin
    a, b = P(0, u.Hb), P(W, 0)
    svg.rect(a[0], a[1], b[0] - a[0], b[1] - a[1], "shell")
    # roof panel and fin, up to the crease where the roof corner bends
    hx, hz = u.hinge
    lx, lz = u.lift_start
    t = (u.ridge - hz) / (lz - hz)
    ridge_x = hx + (lx - hx) * t
    svg.polygon([P(0, u.Hb), P(hx, hz), P(ridge_x, u.ridge), P(0, u.ridge)], "shell", 'style="fill:#d7e7f7"')
    svg.polygon([P(0, u.ridge), P(ridge_x, u.ridge), P(lx, lz), P(0, u.H)], "shell")
    # bent roof corner (between the two creases) and the spout's side flap
    svg.polygon([P(hx, hz), P(lx, lz), P(*u.crease_top)], "shell", 'style="fill:#cfe1f4"')
    svg.polygon([P(hx, hz), P(*u.crease_top), P(u.tip_X, u.tip_z)], "shell")
    for q in (u.lift_start, u.crease_top):
        svg.line(P(hx, hz), P(*q), "dim", 'stroke-dasharray="5 4" style="stroke:#185fa5"')
    # the opening faces up, along the top edge, widest toward the tip
    cx, cz = u.crease_top
    svg.polygon([P(lx + 0.3, lz - 0.05), P(cx, cz - 0.05), P(u.tip_X - 0.25, u.tip_z - 0.05),
                 P(u.tip_X - 1.4, u.tip_z - 0.55), P(cx, cz - 0.45)], "mouth")


def _elev_stairs(u: Upright, svg: SVG, P, upto_flights: int | None = None):
    """Cut-away of the spiral, drawn faintly inside the front face."""
    n = upto_flights or u.n
    for z0, z1, r, run in u.flights[:n]:
        along_x = (r[1] - r[0]) > (r[3] - r[2]) + 1e-6 or abs((r[1] - r[0]) - run) < 1e-6
        if not along_x:
            continue          # flight along an end wall: seen edge-on, skip
        front = r[2] < u.W / 2
        # front wall climbs +X, back wall climbs -X
        x0, x1 = (r[0], r[1]) if front else (r[1], r[0])
        extra = 'opacity="0.8"' if front else 'stroke-dasharray="4 3" opacity="0.55"'
        svg.line(P(x0, z0), P(x1, z1), "rail", extra + ' style="stroke:#ba7517;stroke-width:3"')
    top = u.flights[n - 1][1]
    for z, r, kind in u.lands[1:]:
        if z <= top + 1e-6:
            svg.line(P(r[0], z), P(r[1], z), "rail", 'style="stroke:#854f0b;stroke-width:3"')


def _person(svg: SVG, P, X, z, s=6.0):
    head = P(X, z + s * 0.9)
    svg.circle(head, K * s * 0.08, "person")
    svg.line(P(X, z + s * 0.82), P(X, z + s * 0.45), "person")
    svg.line(P(X, z + s * 0.45), P(X - 0.5, z), "person")
    svg.line(P(X, z + s * 0.45), P(X + 0.5, z), "person")
    svg.line(P(X, z + s * 0.72), P(X - 0.6, z + s * 0.5), "person")
    svg.line(P(X, z + s * 0.72), P(X + 0.6, z + s * 0.5), "person")


def elevation(u: Upright) -> str:
    c, W = u.cfg, u.L
    line = u.side_slide()
    xmax = max(line[-1][0], u.tip_X) + 12
    OX, GY = 130.0, 110 + K * (u.H + 1)
    P = lambda X, z: (OX + K * X, GY - K * z)
    svg = SVG(int(OX + K * xmax + 40), int(GY + 120), "Upright carton, side view",
              "Side view of the upright carton with the stairs cut away and the slide leaving a tear in the spout-end wall.")
    _elev_frame(u, svg, P)
    _elev_stairs(u, svg, P, upto_flights=u.n)
    svg.line(P(c.wall_ft, u.deck_z), P(W - c.wall_ft, u.deck_z), "rail", 'style="stroke:#854f0b;stroke-width:3"')
    hole = [P(W, c.side_outlet_ft - 0.2), P(W, c.side_outlet_ft + 5.5)]
    svg.line(hole[0], hole[1], "rail", 'style="stroke:#042c53;stroke-width:6"')
    _milk(svg, [P(X, z) for X, z in line], True)
    for f in (0.22, 0.45, 0.65):
        X, z = line[int(f * len(line))]
        svg.line(P(X, z - 0.6), P(X, 0), "post")
    ex = line[-1][0]
    svg.add(f'<ellipse class="puddle" cx="{OX + K * (ex + 2):.1f}" cy="{GY - 4:.1f}" rx="{K * 8:.1f}" ry="{K * 1.0:.1f}"/>')
    _person(svg, P, W - 3, c.side_outlet_ft)
    p = P(W + 3, c.side_outlet_ft + 3)
    svg.line(P(W + 0.3, c.side_outlet_ft + 2.5), (p[0] - 4, p[1] - 4), "leader")
    svg.text(p[0], p[1], f"Outlet at {c.side_outlet_ft:g} ft (landing at the spout end): the milk pours out of a tear in the end wall", "s")
    tp = P(u.tip_X + 1, u.tip_z - 1)
    svg.text(tp[0], tp[1], f"Spout open for the look (tip {u.tip_z:.0f} ft)", "s")
    svg.text(24, 30, f"Upright carton, side view: {u.L:.1f} x {u.W:.1f} ft footprint, {u.H:g} ft to the top of the fin", "h")
    svg.text(24, 50, f"Slide drops {c.side_outlet_ft - 0.6:.0f} ft over about {u.side_run:.0f} ft, "
                     f"steepest {u.side_max_deg:.0f}°. Stairs continue up to the eave deck as a lookout.", "s")
    for z, text in ((u.H, f"Fin top {u.H:g} ft"), (u.Hb, f"Walls {u.Hb:g} ft"), (u.deck_z, f"Eave deck {u.deck_z:g} ft")):
        a = P(0, z)
        svg.line((a[0] - 4, a[1]), (a[0] - 30, a[1]), "leader")
        svg.text(a[0] - 34, a[1] + 4, text, "xs", "end")
    _issues(svg, u, 24, GY + 80)
    return svg.render()


def plan(u: Upright) -> str:
    c, W, L, w = u.cfg, u.W, u.L, u.w
    line = u.side_slide()
    out_z, out_r, _ = u.outlet_landing()
    oy = (out_r[2] + out_r[3]) / 2
    KP = 15.0
    xmin, ymin = -4, -5
    xmax, ymax = line[-1][0] + 12, W + 4
    OX, OY = 40 - KP * xmin, 60 + KP * ymax
    P = lambda X, y: (OX + KP * X, OY - KP * y)
    tx = KP * (xmax - xmin) + 110
    svg = SVG(int(tx + 900), int(KP * (ymax - ymin) + 120), "Plan of the spiral stairs",
              "Top-down view of the upright carton: stairs around the four inside walls with landings at the turns.")
    _milk(svg, [P(L, oy), P(line[-1][0], oy)], True, width=KP * 2 * c.slide_half_width_ft)
    for f in (0.22, 0.45, 0.65):
        X = line[int(f * len(line))][0]
        svg.circle(P(X, oy), 3, "post")
    ep = P(line[-1][0] + 2, oy)
    svg.add(f'<ellipse class="puddle" cx="{ep[0]:.1f}" cy="{ep[1]:.1f}" rx="{KP * 8:.1f}" ry="{KP * 5:.1f}"/>')
    svg.text(ep[0], ep[1] + KP * 5 + 16, "Puddle", "s", "middle")
    mp = P((L + line[-1][0]) / 2, oy)
    svg.text(mp[0], mp[1] - KP * 2.2, f"Slide, {u.side_run:.0f} ft", "s", "middle")
    a, b = P(0, W), P(L, 0)
    svg.rect(a[0], a[1], b[0] - a[0], b[1] - a[1], "shell")
    # opened spout seen from above: back point on the ridge, out to the end-wall corners, to the tip
    bx = u.lift_start[0]
    sx = L - c.roof_bend_side_back_ft
    svg.polygon([P(bx, W / 2), P(L, 0), P(u.tip_X, W / 2), P(L, W)], "shell", 'style="fill:#cfe1f4"')
    for yy in (0, W):
        svg.line(P(bx, W / 2), P(sx, yy), "dim", 'stroke-dasharray="5 4" style="stroke:#185fa5"')
    svg.line(P(0, W / 2), P(bx, W / 2), "rail", 'style="stroke:#185fa5;stroke-width:3"')
    # one lap of flights (the plan repeats every lap)
    first_lap = []
    for f in u.flights:
        r = f[2]
        if any(abs(r[0] - g[2][0]) < 1e-6 and abs(r[2] - g[2][2]) < 1e-6 for g in first_lap):
            continue
        first_lap.append(f)
    for z0, z1, r, run in first_lap:
        p0, p1 = P(r[0], r[3]), P(r[1], r[2])
        svg.rect(p0[0], p0[1], p1[0] - p0[0], p1[1] - p0[1], "flight")
    # landings, with every height that uses each spot
    spots = {}
    for z, r, kind in u.lands:
        key = tuple(round(v, 3) for v in r)
        spots.setdefault(key, []).append((z, kind))
    for r, hs in spots.items():
        p0, p1 = P(r[0], r[3]), P(r[1], r[2])
        svg.rect(p0[0], p0[1], p1[0] - p0[0], p1[1] - p0[1], "landing")
        cx, cy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        svg.text(cx, cy - 6, "Entry" if any(k == "entry" for _, k in hs) else "Landing", "xs", "middle")
        svg.text(cx, cy + 9, " / ".join(f"{z:.1f}" for z, _ in hs) + " ft", "xs", "middle")
    # direction arrows along the flights
    for z0, z1, r, run in first_lap:
        cxm, cym = (r[0] + r[1]) / 2, (r[2] + r[3]) / 2
        if abs((r[1] - r[0]) - run) < 1e-6:     # along X
            d = 1 if r[2] < W / 2 else -1
            svg.line(P(cxm - d * run * 0.3, cym), P(cxm + d * run * 0.3, cym), "dim", 'marker-end="url(#arrow)"')
        else:
            d = 1 if r[0] > L / 2 else -1
            svg.line(P(cxm, cym - d * run * 0.3), P(cxm, cym + d * run * 0.3), "dim", 'marker-end="url(#arrow)"')
    # the whole diamond is the opening, open to the sky above the stairs
    svg.polygon([P(bx + 0.35, W / 2), P(L - 0.1, 0.35), P(u.tip_X - 0.35, W / 2), P(L - 0.1, W - 0.35)], "mouth",
                'style="fill-opacity:0.3"')
    op = P((bx + u.tip_X) / 2 + 1.0, W / 2)
    svg.text(op[0], op[1] - 4, "Opening,", "xs", "middle")
    svg.text(op[0], op[1] + 10, "open to sky", "xs", "middle")
    # well
    m0, m1 = P(c.wall_ft + w, W - c.wall_ft - w), P(L - c.wall_ft - w, c.wall_ft + w)
    svg.rect(m0[0], m0[1], m1[0] - m0[0], m1[1] - m0[1], "ground", 'style="fill:#ffffff;stroke-dasharray:4 3"')
    mc = ((m0[0] + m1[0]) / 2 - KP * 3, (m0[1] + m1[1]) / 2)
    svg.text(mc[0], mc[1] - 4, f"Open well {u.well_x:.0f} x {u.well_y:.0f} ft", "xs", "middle")
    svg.text(mc[0], mc[1] + 10, "netted at every lap", "xs", "middle")
    dp = P(c.wall_ft + w / 2, 0)
    svg.line((dp[0], dp[1] + 34), (dp[0], dp[1] + 3), "dim", 'marker-end="url(#arrow)"')
    svg.text(dp[0], dp[1] + 48, "Door", "s", "middle")
    hp = P(L, oy)
    svg.text(hp[0] + 6, hp[1] + KP * 2.6, f"Tear in the end wall at {out_z:.1f} ft", "xs")
    # dimensions
    svg.text((P(0, 0)[0] + P(L, 0)[0]) / 2, P(0, W)[1] - 8, f"{L:.1f} ft", "s", "middle")
    svg.text(P(0, 0)[0] - 8, (P(0, 0)[1] + P(0, W)[1]) / 2, f"{W:.1f} ft", "s", "end")
    lines = [
        ("h", "Spiral stairs"),
        ("s", f"{w:.1f} ft clear, two-way, {u.pitch:.0f}°"),
        ("s", f"{u.n} flights, longest {u.run:.1f} ft;"),
        ("s", "long walls have a mid-wall landing"),
        ("s", f"Longest fall {u.max_rise:.1f} ft (flight to landing)"),
        ("s", f"Eave deck (lookout) at {u.deck_z:g} ft"),
        ("s", ""),
        ("h", "Slide"),
        ("s", f"Out of a tear in the spout-end wall"),
        ("s", f"at the {out_z:.1f} ft landing"),
        ("s", f"About {u.side_run:.0f} ft long, steepest {u.side_max_deg:.0f}°"),
        ("s", ""),
        ("h", "Spout"),
        ("s", f"Open for the look; tip {u.tip_z:.1f} ft"),
    ]
    y = 70
    for cls, t in lines:
        svg.text(tx, y, t, cls)
        y += 20
    _issues(svg, u, tx, y + 10)
    return svg.render()


def _milk(svg: SVG, pts, solid: bool, width: float | None = None):
    from .svgdoc import pts as fmtpts
    sw = width or K * 2.4
    if solid:
        svg.add(f'<polyline class="milk-edge" points="{fmtpts(pts)}" style="stroke-width:{sw + 3:.1f}"/>')
        svg.add(f'<polyline class="milk" points="{fmtpts(pts)}" style="stroke-width:{sw:.1f}"/>')
    else:
        svg.add(f'<polyline class="milk-edge" points="{fmtpts(pts)}" style="stroke-width:{sw:.1f};stroke-dasharray:6 5;opacity:0.6"/>')


def _issues(svg: SVG, u: Upright, x: float, y: float):
    if not u.issues:
        svg.text(x, y, "All checks pass.", "s")
    for level, msg in u.issues:
        color = "#a32d2d" if level == "fail" else "#854f0b"
        tag = {"fail": "FAIL", "open": "OPEN"}.get(level, "NOTE")
        svg.add(f'<text x="{x}" y="{y}" fill="{color}" style="fill:{color}">'
                f'{tag}: {msg.replace("&", "&amp;")}</text>')
        y += 18


def report(u: Upright) -> str:
    c = u.cfg
    u.side_slide()
    out = u.outlet_landing()
    out = [
        "# Upright carton: key numbers", "",
        f"- Carton: {u.L:.1f} x {u.W:.1f} ft footprint (spout on the {u.W:.1f} ft end), walls {u.Hb:g} ft, "
        f"ridge {u.ridge:g} ft, fin top {u.H:g} ft, spout tip {u.tip_z:.1f} ft (open for the look).",
        f"- Spiral stairs: {u.w:.1f} ft clear, {u.n} flights at {u.pitch:.0f}° (longest {u.run:.1f} ft, longest fall "
        f"{u.max_rise:.1f} ft), open well {u.well_x:.0f} x {u.well_y:.0f} ft, eave deck (lookout) {u.deck_z:g} ft.",
        f"- Slide: out of a tear in the spout-end wall at {c.side_outlet_ft:g} ft, about {u.side_run:.0f} ft of run, "
        f"steepest {u.side_max_deg:.0f}°.",
        "", "## Checks", "",
    ]
    out += [f"- {lvl.upper()}: {m}" for lvl, m in u.issues] or ["- All checks pass."]
    return "\n".join(out) + "\n"
