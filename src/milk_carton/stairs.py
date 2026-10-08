"""Zigzag staircase layout and feasibility checks.

The interior of the tipped carton is a V-shaped trough 16 ft deep (y). Its two
sloping surfaces rise faster than any comfortable stair, so the stairs are a
freestanding switchback that crosses the depth of the carton (y) and steps
forward along its length (X) at each turn:

    flight 1  (front -> back)   landing 1 at the back
    flight 2  (back -> front)   landing 2 at the front
    flight 3  (front -> back)   landing 3 at the back  ...

Each landing is `landing_depth_ft` deep and spans two flight widths along X,
because the flight going up and the flight coming down both land on it.
With `flight_skew_ft` > 0 the flights run diagonally instead of straight across.

Plan coordinates are (X, y): X along the carton, y = 0 at the front face
(where the entry door is) and y = width at the back face.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .config import Config
from .geometry import Carton, Point


@dataclass
class Flight:
    idx: int
    z0: float
    z1: float
    poly: list[Point]            # plan outline (X, y)
    path_ft: float               # walking length along the centerline
    pitch_deg: float
    from_side: str               # "front" or "back"
    extent_ft: float             # width of the flight measured along X
    xs: float                    # X of the low end's left edge
    min_clearance_ft: float = math.inf


@dataclass
class Landing:
    idx: int
    z: float
    side: str
    rect: tuple[float, float, float, float]   # x0, x1, y0, y1
    is_launch: bool = False


@dataclass
class Layout:
    cfg: Config
    flights: list[Flight] = field(default_factory=list)
    landings: list[Landing] = field(default_factory=list)
    deck_extra: list[tuple[float, float, float, float]] = field(default_factory=list)
    launch_z: float = 0.0
    x_start: float = 0.0
    x_deck_end: float = 0.0
    issues: list[tuple[str, str]] = field(default_factory=list)   # (level, message)

    @property
    def ok(self) -> bool:
        return not any(level == "fail" for level, _ in self.issues)

    @property
    def max_pitch_deg(self) -> float:
        return max(f.pitch_deg for f in self.flights) if self.flights else 0.0

    @property
    def max_fall_ft(self) -> float:
        return max(f.z1 - f.z0 for f in self.flights) if self.flights else 0.0

    @property
    def min_clearance_ft(self) -> float:
        return min((f.min_clearance_ft for f in self.flights), default=math.inf)

    @property
    def deck_room_ft(self) -> float:
        if not self.landings:
            return 0.0
        last = self.landings[-1]
        return last.rect[1] - last.rect[0]


# ---- small polygon helpers ----------------------------------------------

def _inside(pt: Point, poly: list[Point]) -> bool:
    x, y = pt
    hit = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            hit = not hit
        j = i
    return hit


def _rect_poly(r: tuple[float, float, float, float]) -> list[Point]:
    x0, x1, y0, y1 = r
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def overlap_area(a: list[Point], b: list[Point], step: float = 0.2) -> float:
    xs = [p[0] for p in a]
    ys = [p[1] for p in a]
    count = 0
    x = min(xs) + step / 2
    while x < max(xs):
        y = min(ys) + step / 2
        while y < max(ys):
            if _inside((x, y), a) and _inside((x, y), b):
                count += 1
            y += step
        x += step
    return count * step * step


# ---- layout ---------------------------------------------------------------

def layout(cfg: Config, carton: Carton | None = None) -> Layout:
    carton = carton or Carton(cfg)
    L = Layout(cfg)
    w, Ly, W = cfg.stair_width_ft, cfg.landing_depth, cfg.width_ft
    skew, clr = cfg.flight_skew_ft, cfg.clearance_ft

    spout_X, launch_z = carton.spout_point()
    L.launch_z = launch_z
    n = max(1, math.ceil(launch_z / cfg.landing_interval_ft - 1e-9))
    zs = [0.0] + [min(k * cfg.landing_interval_ft, launch_z) for k in range(1, n)] + [launch_z]

    # where the first flight sits: centered in the V at ground level
    XL, XR = carton.v_range_at(zs[0], clr)
    raw_L, raw_R = carton.v_range_at(zs[0])
    first_extent = _extent(w, _run(1, n, W, Ly), skew)
    room = XR - XL
    if room < first_extent:
        L.issues.append(("fail", f"At grade the V is only {raw_R - raw_L:.1f} ft wide and {room:.1f} ft once "
                                 f"{clr:.1f} ft of clearance is kept; a {w:.1f} ft flight does not fit."))
    x = XL + max(0.0, (room - first_extent) / 2)
    L.x_start = x

    xs_list, ext_list = [], []
    for k in range(1, n + 1):
        run = _run(k, n, W, Ly)
        e = _extent(w, run, skew)
        xs_list.append(x)
        ext_list.append(e)
        x += skew + e

    for k in range(1, n + 1):
        run = _run(k, n, W, Ly)
        e, xs = ext_list[k - 1], xs_list[k - 1]
        y_s, y_e = _ys(k, W, Ly)
        poly = [(xs, y_s), (xs + e, y_s), (xs + skew + e, y_e), (xs + skew, y_e)]
        path = math.hypot(run, skew)
        rise = zs[k] - zs[k - 1]
        pitch = math.degrees(math.atan2(rise, path)) if path > 1e-6 else 90.0
        f = Flight(k, zs[k - 1], zs[k], poly, path, pitch,
                   "front" if y_s < W / 2 else "back", e, xs)
        if run < 1.0:
            L.issues.append(("fail", f"Flight {k} has only {run:.1f} ft of run between landings."))
        if pitch > cfg.max_pitch_deg:
            L.issues.append(("fail", f"Flight {k} pitch is {pitch:.0f} deg (max {cfg.max_pitch_deg:.0f})."))
        elif pitch > cfg.comfort_pitch_deg:
            L.issues.append(("warn", f"Flight {k} pitch is {pitch:.0f} deg (comfort limit {cfg.comfort_pitch_deg:.0f})."))
        # clearance to the carton surfaces along the flight
        for i in range(21):
            t = i / 20
            z = f.z0 + t * rise
            lo, hi = xs + skew * t, xs + skew * t + e
            c = math.inf
            fz = carton.floor_z(hi)
            if fz is not None:
                c = min(c, z - fz)
            if lo < 0:
                pz = carton.panel_z(lo)
                if pz is not None:
                    c = min(c, z - pz)
            f.min_clearance_ft = min(f.min_clearance_ft, c)
        if f.min_clearance_ft < clr - 1e-6:
            L.issues.append(("fail", f"Flight {k} comes within {f.min_clearance_ft:.2f} ft of the carton surface "
                                     f"(need {clr:.1f})."))
        L.flights.append(f)

    # landings
    x_end = spout_X - 0.5
    L.x_deck_end = x_end
    for k in range(1, n + 1):
        side = "back" if k % 2 == 1 else "front"
        y0, y1 = (W - Ly, W) if side == "back" else (0.0, Ly)
        x0 = xs_list[k - 1] + skew
        x1 = (xs_list[k] + ext_list[k]) if k < n else x_end
        if k == n and x1 - x0 < w:
            L.issues.append(("fail", f"Only {x1 - x0:.1f} ft between the last flight and the spout for the launch deck "
                                     f"(need at least {w:.1f})."))
        lz = zs[k]
        ln = Landing(k, lz, side, (x0, x1, y0, y1), is_launch=(k == n))
        # clearance under the landing's high end
        fz = carton.floor_z(x1)
        if fz is not None and lz - fz < clr - 1e-6:
            L.issues.append(("fail", f"Landing {k} sits {lz - fz:.2f} ft above the carton surface (need {clr:.1f})."))
        L.landings.append(ln)

    # bridge from the launch deck over to the centered spout
    last = L.landings[-1]
    cx0 = max(last.rect[0], last.rect[1] - w)
    if last.side == "back":
        L.deck_extra.append((cx0, last.rect[1], W / 2 - w / 2, W - Ly))
    else:
        L.deck_extra.append((cx0, last.rect[1], Ly, W / 2 + w / 2))

    # stacked flights need headroom: no two surfaces closer than headroom_ft may overlap in plan
    surfaces = [(f"flight {f.idx}", f.poly, (f.z0 + f.z1) / 2, f.z0, f.z1) for f in L.flights]
    surfaces += [(f"landing {l.idx}", _rect_poly(l.rect), l.z, l.z, l.z) for l in L.landings]
    for i in range(len(surfaces)):
        for j in range(i + 1, len(surfaces)):
            na, pa, _, a0, a1 = surfaces[i]
            nb, pb, _, b0, b1 = surfaces[j]
            gap = max(b0 - a1, a0 - b1, 0.0)
            if gap >= cfg.headroom_ft:
                continue
            area = overlap_area(pa, pb)
            if area > 0.3:
                L.issues.append(("fail", f"{na} and {nb} overlap in plan ({area:.1f} sq ft) with only "
                                         f"{gap:.1f} ft between them (need {cfg.headroom_ft:.1f})."))
    return L


def _ys(k: int, W: float, Ly: float) -> tuple[float, float]:
    """Lateral start and end of flight k. Odd flights go front->back."""
    if k % 2 == 1:
        return (0.0 if k == 1 else Ly), W - Ly
    return W - Ly, Ly


def _run(k: int, n: int, W: float, Ly: float) -> float:
    y_s, y_e = _ys(k, W, Ly)
    return abs(y_e - y_s)


def _extent(w: float, run: float, skew: float) -> float:
    """Width of a flight measured along X, so that its width perpendicular to travel is w."""
    phi = math.atan2(skew, max(run, 1e-6))
    return w / math.cos(phi)


# ---- sweeps -----------------------------------------------------------------

def sweep(cfg: Config, widths=(4.0, 4.5, 5.0, 5.5, 6.0), intervals=(3.0, 4.0, 5.0), skew=None):
    """Try every width/landing-interval combination and summarize what holds up."""
    rows = []
    for w in widths:
        for iv in intervals:
            changes = dict(stair_width_ft=w, landing_interval_ft=iv, landing_depth_ft=None)
            if skew is not None:
                changes["flight_skew_ft"] = skew
            c = cfg.replace(**changes)
            lay = layout(c)
            fails = [m for lvl, m in lay.issues if lvl == "fail"]
            rows.append(dict(width=w, interval=iv, flights=len(lay.flights),
                             worst_pitch=lay.max_pitch_deg, max_fall=lay.max_fall_ft,
                             deck_room=lay.deck_room_ft, ok=lay.ok,
                             first_problem=(fails[0] if fails else "")))
    return rows
