"""Explainer: how the gable-top spout opens, closed vs opened, full carton height.

Side view (whole carton, to scale) and top view, both drawn from the Upright
model so they always match the other schematics.
"""

from __future__ import annotations

from .svgdoc import SVG
from .upright import Upright

K = 11.0      # px per ft, side view
KT = 9.0      # px per ft, top view


def render(u: Upright) -> str:
    c, W, L, E, R, H = u.cfg, u.W, u.L, u.Hb, u.ridge, u.H
    side_h = K * (u.tip_z + 1)
    top_y0 = 140 + side_h + 50
    height = int(top_y0 + KT * W + 60)
    svg = SVG(1280, height, "How the spout opens",
              "Side and top views of the carton, closed and opened, to scale.")
    svg.text(24, 30, "How the spout opens (whole carton, to scale)", "h")
    svg.text(24, 50, f"{L:.1f} x {W:.1f} ft footprint (spout on the {W:.1f} ft end), walls {E:g} ft, fin top {H:g} ft: the roof and fin are the top "
                     f"{100 * (H - E) / H:.0f}% of the carton.", "s")
    svg.text(24, 68, "Opened: the end of the gable swings out on a hinge at the top of the wall. The roof corners and "
                     "side flaps bend along the dashed creases, and the whole diamond on top is the opening.", "s")

    for i, opened in enumerate([False, True]):
        ox = 50 + i * 600
        base = 140 + side_h
        P = lambda X, z, ox=ox, base=base: (ox + K * X, base - K * z)
        svg.text(ox, 100, "Opened" if opened else "Closed", "h")
        svg.text(ox, 118, "Side view", "xs")
        svg.line((ox - 20, base), (ox + K * (L + 8), base), "dim")
        svg.polygon([P(0, 0), P(L, 0), P(L, E), P(0, E)], "shell")
        if not opened:
            svg.polygon([P(0, E), P(L, E), P(L, R), P(0, R)], "shell", 'style="fill:#d7e7f7"')
            svg.polygon([P(0, R), P(L, R), P(L, H), P(0, H)], "shell")
        else:
            hx, hz = u.hinge
            lx, lz = u.lift_start
            cx, cz = u.crease_top
            t = (R - hz) / (lz - hz)
            rx = hx + (lx - hx) * t
            svg.polygon([P(0, E), P(hx, hz), P(rx, R), P(0, R)], "shell", 'style="fill:#d7e7f7"')
            svg.polygon([P(0, R), P(rx, R), P(lx, lz), P(0, H)], "shell")
            svg.polygon([P(hx, hz), P(lx, lz), P(cx, cz)], "shell", 'style="fill:#cfe1f4"')
            svg.polygon([P(hx, hz), P(cx, cz), P(u.tip_X, u.tip_z)], "shell")
            for q in (u.lift_start, u.crease_top):
                svg.line(P(hx, hz), P(*q), "dim", 'stroke-dasharray="5 4" style="stroke:#185fa5"')
            svg.polygon([P(lx + 0.3, lz - 0.05), P(cx, cz - 0.05), P(u.tip_X - 0.25, u.tip_z - 0.05),
                         P(u.tip_X - 1.4, u.tip_z - 0.55), P(cx, cz - 0.45)], "mouth")
            tp = P(u.tip_X, u.tip_z)
            svg.text(tp[0] + 8, tp[1] + 4, f"tip {u.tip_z:.1f} ft, {u.tip_X - L:.1f} ft out", "xs")
            hp = P(hx, hz)
            svg.text(hp[0] + 8, hp[1] + 4, f"hinge at the top of the wall ({E:g} ft)", "xs")
        # height marks
        for z, label in ((E, f"{E:g} ft"), (H, f"{H:g} ft")):
            a = P(0, z)
            svg.text(a[0] - 6, a[1] + 4, label, "xs", "end")

        # top view, to scale
        Q = lambda X, y, ox=ox: (ox + KT * X, top_y0 + KT * (W - y))
        svg.text(ox, top_y0 - 12, "Top view", "xs")
        svg.polygon([Q(0, 0), Q(L, 0), Q(L, W), Q(0, W)], "shell")
        if not opened:
            svg.line(Q(0, W / 2), Q(L, W / 2), "rail", 'style="stroke:#185fa5;stroke-width:3"')
        else:
            bx, sx = u.lift_start[0], L - c.roof_bend_side_back_ft
            svg.polygon([Q(bx, W / 2), Q(L, 0), Q(u.tip_X, W / 2), Q(L, W)], "shell", 'style="fill:#cfe1f4"')
            for yy in (0, W):
                svg.line(Q(bx, W / 2), Q(sx, yy), "dim", 'stroke-dasharray="5 4" style="stroke:#185fa5"')
            svg.line(Q(0, W / 2), Q(bx, W / 2), "rail", 'style="stroke:#185fa5;stroke-width:3"')
            svg.polygon([Q(bx + 0.35, W / 2), Q(L - 0.1, 0.35), Q(u.tip_X - 0.35, W / 2), Q(L - 0.1, W - 0.35)],
                        "mouth")
            e = Q(u.tip_X, W / 2)
            svg.text(e[0] + 8, e[1] + 4, "the whole diamond is open (faces up)", "xs")
            b = Q(bx, W / 2)
            svg.text(b[0] - 4, b[1] - 46, "fin starts lifting", "xs", "end")
            svg.line((b[0] - 30, b[1] - 42), (b[0], b[1] - 3), "leader")
    return svg.render()
