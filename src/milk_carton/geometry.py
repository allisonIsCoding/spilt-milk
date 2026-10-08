"""Carton geometry.

Two coordinate systems are used throughout:

* local  (u, v): across and along the carton, before it is tipped.
  v runs from the base corner up the body, u runs across the width and is 0
  at the wall the carton tips toward (the "right wall"), negative to the left.
* world  (X, z): after tipping. X is horizontal distance from the base corner,
  z is height above grade (grade is `sink_ft` above the base corner).

The third direction, y, runs across the carton's depth (into the page in the
side view) and only appears in the stair plan.
"""

from __future__ import annotations

import math
from typing import Sequence

from .config import Config

Point = tuple[float, float]


def _interp(pts: Sequence[Point], x: float) -> float | None:
    """Piecewise-linear lookup on a polyline sorted by x."""
    if x < pts[0][0] - 1e-9 or x > pts[-1][0] + 1e-9:
        return None
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 - 1e-9 <= x <= x1 + 1e-9:
            if abs(x1 - x0) < 1e-12:
                return y0
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return None


def bezier(p0: Point, p1: Point, p2: Point, p3: Point, n: int = 40) -> list[Point]:
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t**2, t**3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


# Slide centerline, as fractions of (run, drop) from the mouth to the run-out.
# Traced from the hand-drawn "purple" line: leaves nearly level, rolls over a
# lip, drops steeply, then eases out flat. Three cubic Bezier segments.
SLIDE_SHAPE = [
    ((0.1316, -0.0089), (0.2697, 0.0982), (0.3421, 0.3304)),
    ((0.4079, 0.5268), (0.4737, 0.7768), (0.6711, 0.9286)),
    ((0.7697, 1.0000), (0.8355, 1.0000), (1.0000, 1.0000)),
]

# Outline of the puddle, in feet relative to the end of the slide at grade.
# (x, height above grade), as one closed cubic path: M p0 C c c p C c c p ...
PUDDLE = [
    (-7.2, 1.6),
    ((-6.25, 3.0), (-0.8, 3.1), (2.3, 2.65)),
    ((6.25, 2.3), (8.75, 1.1), (6.7, 0.16)),
    ((3.9, -0.8), (-3.9, -0.8), (-7.2, 0.3)),
]


class Carton:
    def __init__(self, cfg: Config):
        cfg.validate()
        self.cfg = cfg
        self.t = math.radians(cfg.tilt_deg)
        self.c, self.s = math.cos(self.t), math.sin(self.t)
        self.W, self.Hb, self.R, self.H = cfg.width_ft, cfg.body_ft, cfg.roof_ft, cfg.height_ft
        self.sink = cfg.sink_ft
        self.tip = cfg.beak_ft

    # ---- transforms ------------------------------------------------------
    def to_world(self, u: float, v: float) -> Point:
        return (u * self.c + v * self.s, v * self.c - u * self.s - self.sink)

    # ---- shell -----------------------------------------------------------
    def body_local(self) -> list[Point]:
        return [(-self.W, 0), (0, 0), (0, self.Hb), (-self.W, self.Hb)]

    def roof_local(self) -> list[Point]:
        c = self.cfg
        return [(-self.W, self.Hb), (-self.W + c.ridge_inset_ft, self.Hb + self.R),
                (-self.W + c.ridge_inset_ft, self.H), (self.tip, self.H), (0, self.Hb)]

    def ridge_line_local(self) -> tuple[Point, Point]:
        c = self.cfg
        return ((-self.W + c.ridge_inset_ft, self.Hb + self.R),
                (self.tip - c.mouth_len_ft - 0.4, self.Hb + self.R))

    def mouth_local(self) -> list[Point]:
        c = self.cfg
        top = self.H - 0.5
        return [(self.tip - c.mouth_len_ft, top), (self.tip - 0.4, top),
                (self.tip - 1.4, top - c.mouth_depth_ft)]

    def to_world_poly(self, pts: Sequence[Point]) -> list[Point]:
        return [self.to_world(u, v) for u, v in pts]

    # ---- floor -----------------------------------------------------------
    def floor_profile(self) -> list[Point]:
        """Inner climbing surface in world coords: up the wall, then the roof edge."""
        return [self.to_world(0, 0), self.to_world(0, self.Hb), self.to_world(self.tip, self.H)]

    def panel_profile(self) -> list[Point]:
        """The old bottom panel, which now slopes up to the left."""
        return [self.to_world(-self.W, 0), self.to_world(0, 0)]

    def floor_z(self, X: float) -> float | None:
        return _interp(self.floor_profile(), X)

    def panel_z(self, X: float) -> float | None:
        return _interp(self.panel_profile(), X)

    @property
    def floor_slope_deg(self) -> float:
        return 90.0 - self.cfg.tilt_deg

    @property
    def panel_slope_deg(self) -> float:
        return self.cfg.tilt_deg

    def floor_cross_grade_X(self) -> float:
        """X where the climbing surface comes out of the ground."""
        return self.sink * math.tan(self.t)

    def panel_cross_grade_X(self) -> float:
        return -self.sink / math.tan(self.t)

    def v_range_at(self, z: float, clearance: float = 0.0) -> Point:
        """Horizontal extent of the V-shaped trough at height z above grade.

        With a clearance, the range is the X interval where a surface at height z
        stays at least that far (vertically) above both sloping walls.
        """
        s = z + self.sink - clearance
        return (-s / math.tan(self.t), s * math.tan(self.t))

    # ---- spout and slide -------------------------------------------------
    def mouth_world(self) -> list[Point]:
        return self.to_world_poly(self.mouth_local())

    def spout_point(self) -> Point:
        """Where the slide starts: the middle of the open end of the mouth."""
        _, b, c = self.mouth_local()
        return self.to_world((b[0] + c[0]) / 2, (b[1] + c[1]) / 2)

    def tip_world(self) -> Point:
        return self.to_world(self.tip, self.H)

    def slide_path(self) -> list[tuple[Point, Point, Point, Point]]:
        """Cubic segments of the slide centerline in world coords."""
        x0, z0 = self.spout_point()
        drop = z0 - self.cfg.slide_half_width_ft
        run = self.cfg.slide_run_ft

        def pt(f):
            return (x0 + f[0] * run, z0 - f[1] * drop)

        segs, start = [], (x0, z0)
        for c1, c2, p in SLIDE_SHAPE:
            segs.append((start, pt(c1), pt(c2), pt(p)))
            start = pt(p)
        return segs

    def slide_polyline(self, n: int = 40) -> list[Point]:
        out: list[Point] = []
        for seg in self.slide_path():
            out.extend(bezier(*seg, n=n))
        return out

    def slide_z_at(self, X: float) -> float:
        pts = self.slide_polyline(120)
        best = min(pts, key=lambda p: abs(p[0] - X))
        return best[1]

    def slide_end(self) -> Point:
        return self.slide_path()[-1][3]

    def slide_max_slope_deg(self) -> float:
        pts = self.slide_polyline(200)
        worst = 0.0
        for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
            if x1 - x0 > 1e-6:
                worst = max(worst, math.degrees(math.atan2(z0 - z1, x1 - x0)))
        return worst

    def slide_length_ft(self) -> float:
        pts = self.slide_polyline(200)
        return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))

    # ---- misc ------------------------------------------------------------
    def top_height(self) -> float:
        zs = [p[1] for p in self.to_world_poly(self.roof_local())]
        return max(zs)

    def left_extent(self) -> float:
        return min(p[0] for p in self.to_world_poly(self.body_local()))
