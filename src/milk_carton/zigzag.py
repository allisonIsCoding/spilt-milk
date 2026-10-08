"""Diagonal zigzag stairs: landings on alternating sides, flights running
diagonally across the carton between them (a /\\/\\ shape seen from above).

    door (front face, grade) -> landing 1 (back) -> landing 2 (front) -> ... -> launch deck

Each flight is a straight band `stair_width_ft` wide running from the centre of
one landing to the centre of the next; the landings sit on top of the ends.
Landings are `landing_size_ft` square. Their positions along the carton (X)
come from `landing_x_ft` in the config, or are chosen automatically to give
the gentlest stairs that pass every check.

Plan coordinates are (X, y): X along the carton, y = 0 at the front face
(where the entry door is) and y = width at the back face.
"""

from __future__ import annotations

import itertools
import math

from .config import Config
from .geometry import Carton, Point
from .stairs import Flight, Landing, Layout

RISER_FT = 0.6      # first tread height: the flight's surface starts one riser above grade
STEP = 0.25         # plan sampling grid for the checks, ft


# ---- geometry helpers -------------------------------------------------------

def _rect(cx: float, cy: float, size: float, W: float) -> tuple[float, float, float, float]:
    y0 = min(max(cy - size / 2, 0.0), W - size)
    return (cx - size / 2, cx + size / 2, y0, y0 + size)


def _in_rect(p: Point, r) -> bool:
    return r[0] <= p[0] <= r[1] and r[2] <= p[1] <= r[3]


def _exit_t(a: Point, b: Point, r) -> float:
    """Fraction along a->b where the segment leaves rectangle r (a is inside r)."""
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        p = (a[0] + (b[0] - a[0]) * mid, a[1] + (b[1] - a[1]) * mid)
        if _in_rect(p, r):
            lo = mid
        else:
            hi = mid
    return lo


class _Band:
    """One flight: a band of width w along the segment a->b, rising z0->z1
    between where it leaves rectangle ra and enters rectangle rb."""

    def __init__(self, a: Point, b: Point, w: float, z0: float, z1: float, ra, rb):
        self.a, self.b, self.w, self.z0, self.z1, self.ra, self.rb = a, b, w, z0, z1, ra, rb
        dx, dy = b[0] - a[0], b[1] - a[1]
        self.len = math.hypot(dx, dy)
        self.u = (dx / self.len, dy / self.len)
        self.n = (-self.u[1], self.u[0])
        self.ta = _exit_t(a, b, ra) if ra else 0.0
        self.tb = 1.0 - _exit_t(b, a, rb)
        self.path = max(1e-6, (self.tb - self.ta) * self.len)
        self.pitch = math.degrees(math.atan2(z1 - z0, self.path))

    def covers(self, p: Point) -> bool:
        rx, ry = p[0] - self.a[0], p[1] - self.a[1]
        s = rx * self.u[0] + ry * self.u[1]
        d = rx * self.n[0] + ry * self.n[1]
        return 0 <= s <= self.len and abs(d) <= self.w / 2 + 1e-9

    def section(self, t: float, k: int = 11) -> list[Point]:
        """Points across the band's width at fraction t along it."""
        cx, cy = self.a[0] + (self.b[0] - self.a[0]) * t, self.a[1] + (self.b[1] - self.a[1]) * t
        h = self.w / 2
        return [(cx + self.n[0] * h * (2 * i / (k - 1) - 1), cy + self.n[1] * h * (2 * i / (k - 1) - 1))
                for i in range(k)]

    def strip(self, t0: float, t1: float) -> list[Point]:
        """Plan outline of the band between fractions t0 and t1."""
        h = self.w / 2
        def at(t, sgn):
            return (self.a[0] + (self.b[0] - self.a[0]) * t + sgn * self.n[0] * h,
                    self.a[1] + (self.b[1] - self.a[1]) * t + sgn * self.n[1] * h)
        return [at(t0, -1), at(t0, 1), at(t1, 1), at(t1, -1)]

    def refresh(self) -> None:
        self.path = max(1e-6, (self.tb - self.ta) * self.len)
        self.pitch = math.degrees(math.atan2(self.z1 - self.z0, self.path))

    def poly(self) -> list[Point]:
        h = self.w / 2
        a, b, n = self.a, self.b, self.n
        return [(a[0] - n[0] * h, a[1] - n[1] * h), (a[0] + n[0] * h, a[1] + n[1] * h),
                (b[0] + n[0] * h, b[1] + n[1] * h), (b[0] - n[0] * h, b[1] - n[1] * h)]

    def z_at(self, p: Point) -> float | None:
        """Height of the walking surface at plan point p, or None if p is off the band
        (or under one of its end landings)."""
        rx, ry = p[0] - self.a[0], p[1] - self.a[1]
        s = rx * self.u[0] + ry * self.u[1]
        d = rx * self.n[0] + ry * self.n[1]
        if s < 0 or s > self.len or abs(d) > self.w / 2:
            return None
        if (self.ra and _in_rect(p, self.ra)) or (self.rb and _in_rect(p, self.rb)):
            return None
        t = s / self.len
        f = min(1.0, max(0.0, (t - self.ta) / max(1e-9, self.tb - self.ta)))
        return self.z0 + f * (self.z1 - self.z0)


# ---- layout -----------------------------------------------------------------

def levels(cfg: Config, launch_z: float) -> list[float]:
    n = max(1, math.ceil(launch_z / cfg.landing_interval_ft - 1e-9))
    return [0.0] + [k * cfg.landing_interval_ft for k in range(1, n)] + [launch_z]


def build(cfg: Config, carton: Carton, door_x: float, xs: list[float], check: bool = True,
          step: float = STEP) -> Layout:
    """Lay out the stairs with the door at door_x and landing centres at xs."""
    W, w, Ls = cfg.width_ft, cfg.stair_width_ft, cfg.landing_size_ft
    clr, head = cfg.clearance_ft, cfg.headroom_ft
    spout_X, launch_z = carton.spout_point()
    zs = levels(cfg, launch_z)
    n = len(zs) - 1
    L = Layout(cfg)
    L.launch_z = launch_z

    # nodes: door, landings on alternating sides (back first), launch deck by the spout
    nodes: list[tuple[Point, tuple | None]] = [((door_x, 0.0), None)]
    for k in range(1, n):
        side_y = W - Ls / 2 if k % 2 == 1 else Ls / 2
        nodes.append(((xs[k - 1], side_y), _rect(xs[k - 1], side_y, Ls, W)))
    x1 = spout_X - 0.5
    deck = (x1 - Ls, x1, W / 2 - Ls / 2, W / 2 + Ls / 2)
    nodes.append((((deck[0] + deck[1]) / 2, W / 2), deck))
    L.x_start, L.x_deck_end = door_x, x1

    bands = [_Band(nodes[k - 1][0], nodes[k][0], w, zs[k - 1], zs[k], nodes[k - 1][1], nodes[k][1])
             for k in range(1, n + 1)]
    # Where two flights meet at a landing they overlap for a while beyond it (the notch in
    # a /\ seen from above). That overlap has to be flat landing, so each flight's sloped
    # part starts or ends where it clears its neighbour.
    junctions = []
    for k in range(n - 1):
        inc, out = bands[k], bands[k + 1]
        r = nodes[k + 1][1]
        def clash(band, other, t):
            return any(other.covers(p) and not _in_rect(p, r) for p in band.section(t))
        t = inc.tb
        while t > inc.ta and clash(inc, out, t):
            t -= 0.05 / inc.len
        if t < inc.tb - 1e-9:
            junctions.append(inc.strip(t, inc.tb))
            inc.tb = t
        t = out.ta
        while t < out.tb and clash(out, inc, t):
            t += 0.05 / out.len
        if t > out.ta + 1e-9:
            junctions.append(out.strip(out.ta, t))
            out.ta = t
    for band in bands:
        band.refresh()
    L.junctions = junctions

    for k, band in enumerate(bands, start=1):
        (a, ra) = nodes[k - 1]
        poly = band.poly()
        frm = "front" if a[1] < W / 2 else "back"
        xs_lo = min(p[0] for p in poly)
        L.flights.append(Flight(k, zs[k - 1], zs[k], poly, band.path, band.pitch, frm,
                                max(p[0] for p in poly) - xs_lo, xs_lo))
    for k in range(1, n + 1):
        (c, r) = nodes[k]
        side = "launch" if k == n else ("back" if c[1] > W / 2 else "front")
        L.landings.append(Landing(k, zs[k], side, r, is_launch=(k == n)))

    if not check:
        return L

    # pitch
    for f in L.flights:
        if f.path_ft < 2.0:
            L.issues.append(("fail", f"Flight {f.idx} has only {f.path_ft:.1f} ft of run."))
        if f.pitch_deg > cfg.max_pitch_deg:
            L.issues.append(("fail", f"Flight {f.idx} pitch is {f.pitch_deg:.0f} deg (max {cfg.max_pitch_deg:.0f})."))
        elif f.pitch_deg > cfg.comfort_pitch_deg:
            L.issues.append(("warn", f"Flight {f.idx} pitch is {f.pitch_deg:.0f} deg (comfort limit {cfg.comfort_pitch_deg:.0f})."))

    # sample every surface on a plan grid
    surfaces = [(f"Flight {k + 1}", bands[k].z_at) for k in range(n)]
    for ln in L.landings:
        r, z = ln.rect, ln.z
        name = "Launch deck" if ln.is_launch else f"Landing {ln.idx}"
        surfaces.append((name, (lambda p, r=r, z=z: z if _in_rect(p, r) else None)))
    xmin = min(min(p[0] for p in f.poly) for f in L.flights) - 1
    xmax = deck[1] + 1
    low_clear = {}
    clash = {}
    shell_lo, shell_hi = carton.panel_profile()[0][0], carton.floor_profile()[-1][0]
    X = xmin
    while X <= xmax:
        y = step / 2
        while y < W:
            here = []
            for name, zf in surfaces:
                z = zf((X, y))
                if z is None:
                    continue
                here.append((z, name))
                ze = max(z, RISER_FT) if name == "Flight 1" else z
                if X < shell_lo or X > shell_hi:
                    c = -99.0
                else:
                    c = math.inf
                    fz = carton.floor_z(X) if X >= 0 else None
                    pz = carton.panel_z(X) if X < 0 else None
                    if fz is not None:
                        c = min(c, ze - fz)
                    if pz is not None:
                        c = min(c, ze - pz)
                low_clear[name] = min(low_clear.get(name, math.inf), c)
            here.sort()
            for (za, na), (zb, nb) in itertools.combinations(here, 2):
                dz = abs(zb - za)
                if 0.1 < dz < head:
                    key = (na, nb) if na < nb else (nb, na)
                    a0, m = clash.get(key, (0.0, head))
                    clash[key] = (a0 + step * step, min(m, dz))
            y += step
        X += step

    for k, f in enumerate(L.flights):
        f.min_clearance_ft = low_clear.get(f"Flight {k + 1}", math.inf)
    for name, c in low_clear.items():
        if c < clr - 1e-6:
            what = "goes outside the carton" if c <= -99 else f"comes within {c:.2f} ft of the carton surface (need {clr:.1f})"
            L.issues.append(("fail", f"{name} {what}."))
    for (na, nb), (area, m) in clash.items():
        if area > 0.3:
            L.issues.append(("fail", f"{na} and {nb} overlap in plan ({area:.1f} sq ft) with only {m:.1f} ft "
                                     f"of headroom (need {cfg.headroom_ft:.1f})."))
    return L


def score(L: Layout) -> tuple:
    """Lower is better: passing first, then gentlest worst flight, then most clearance."""
    fails = sum(1 for lvl, _ in L.issues if lvl == "fail")
    return (fails, round(L.max_pitch_deg, 1), -round(min(L.min_clearance_ft, 5.0), 2))


def auto_place(cfg: Config, carton: Carton) -> tuple[float, list[float]]:
    """Search door and landing positions for the gentlest layout that passes."""
    spout_X, launch_z = carton.spout_point()
    n = len(levels(cfg, launch_z)) - 1
    Ls = cfg.landing_size_ft
    deck_cx = spout_X - 0.5 - Ls / 2
    lo_v, hi_v = carton.panel_cross_grade_X(), carton.floor_cross_grade_X()
    doors = [round(lo_v + (hi_v - lo_v) * f, 2) for f in (0.35, 0.5, 0.65)]
    best = None
    # landing centres strictly increase between the door and the deck
    grid = [x / 2 for x in range(int(2 * (lo_v)), int(2 * deck_cx))]
    for d in doors:
        def rec(prefix):
            nonlocal best
            if len(prefix) == n - 1:
                L = build(cfg, carton, d, prefix, step=0.5)
                s = score(L)
                if best is None or s < best[0]:
                    best = (s, d, list(prefix))
                return
            last = prefix[-1] if prefix else d
            for x in grid:
                if x <= last + 1.0 or x > deck_cx - 2.0:
                    continue
                # cheap prune: the landing's high edge must stay above the floor
                z = cfg.landing_interval_ft * (len(prefix) + 1)
                fz = carton.floor_z(x + Ls / 2)
                if fz is not None and z - fz < cfg.clearance_ft:
                    continue
                rec(prefix + [x])
        rec([])
    return best[1], best[2]


def layout(cfg: Config, carton: Carton | None = None) -> Layout:
    carton = carton or Carton(cfg)
    if cfg.landing_x_ft:
        door = cfg.door_x_ft if cfg.door_x_ft is not None else (
            (carton.panel_cross_grade_X() + carton.floor_cross_grade_X()) / 2)
        return build(cfg, carton, door, list(cfg.landing_x_ft))
    door, xs = auto_place(cfg, carton)
    return build(cfg, carton, door, xs)
