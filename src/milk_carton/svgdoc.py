"""A very small SVG writer. No dependencies, just strings."""

from __future__ import annotations

from html import escape
from typing import Iterable, Sequence

STYLE = """
text { font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; fill: #3d3d3a; font-size: 13px; }
.h { font-size: 15px; font-weight: 600; fill: #2c2c2a; }
.s { fill: #5f5e5a; }
.xs { fill: #5f5e5a; font-size: 11.5px; }
.leader { stroke: #888780; stroke-width: 1; stroke-dasharray: 3 3; fill: none; }
.dim { stroke: #888780; stroke-width: 1; fill: none; }
.shell { fill: #e6f1fb; stroke: #185fa5; stroke-width: 1.4; stroke-linejoin: round; }
.mouth { fill: #042c53; }
.ground { fill: #f1efe8; stroke: #b4b2a9; stroke-width: 1; }
.footing { fill: none; stroke: #888780; stroke-width: 1; stroke-dasharray: 5 4; }
.flight { fill: #fac775; fill-opacity: 0.75; stroke: #ba7517; stroke-width: 0.8; }
.landing { fill: #faeeda; stroke: #854f0b; stroke-width: 1; }
.rail { stroke: #888780; stroke-width: 1.4; fill: none; }
.post { stroke: #888780; stroke-width: 1.4; fill: none; }
.door { fill: none; stroke: #854f0b; stroke-width: 1.4; stroke-dasharray: 4 3; }
.milk { fill: none; stroke: #f4f8fc; stroke-linecap: round; }
.milk-edge { fill: none; stroke: #85b7eb; stroke-linecap: round; }
.puddle { fill: #f4f8fc; stroke: #85b7eb; stroke-width: 1; }
.person { stroke: #888780; stroke-width: 1.6; fill: none; stroke-linecap: round; }
"""


def fmt(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


def pts(points: Iterable[Sequence[float]]) -> str:
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)


class SVG:
    def __init__(self, width: int, height: int, title: str, desc: str = ""):
        self.w, self.h = width, height
        self.title, self.desc = title, desc
        self.items: list[str] = []
        self.defs = (
            '<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" '
            'orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" '
            'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker>'
        )

    def add(self, s: str) -> None:
        self.items.append(s)

    def polygon(self, points, cls: str, extra: str = "") -> None:
        self.add(f'<polygon class="{cls}" points="{pts(points)}" {extra}/>')

    def line(self, p, q, cls: str = "dim", extra: str = "") -> None:
        self.add(f'<line class="{cls}" x1="{fmt(p[0])}" y1="{fmt(p[1])}" x2="{fmt(q[0])}" y2="{fmt(q[1])}" {extra}/>')

    def rect(self, x, y, w, h, cls: str, extra: str = "") -> None:
        self.add(f'<rect class="{cls}" x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" {extra}/>')

    def circle(self, c, r, cls: str, extra: str = "") -> None:
        self.add(f'<circle class="{cls}" cx="{fmt(c[0])}" cy="{fmt(c[1])}" r="{fmt(r)}" {extra}/>')

    def path(self, d: str, cls: str, extra: str = "") -> None:
        self.add(f'<path class="{cls}" d="{d}" {extra}/>')

    def text(self, x, y, s: str, cls: str = "", anchor: str = "start") -> None:
        self.add(f'<text class="{cls}" x="{fmt(x)}" y="{fmt(y)}" text-anchor="{anchor}">{escape(s)}</text>')

    def render(self) -> str:
        body = "\n".join(self.items)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" role="img">\n'
            f"<title>{escape(self.title)}</title>\n<desc>{escape(self.desc)}</desc>\n"
            f"<defs>{self.defs}</defs>\n<style>{STYLE}</style>\n"
            f'<rect width="{self.w}" height="{self.h}" fill="#fcfbf8"/>\n{body}\n</svg>\n'
        )
