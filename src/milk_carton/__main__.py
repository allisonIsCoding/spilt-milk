"""Command line: python -m milk_carton [--config FILE] [--set key=value ...] [--out DIR]"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import elevation, plan, report
from .config import Config
from .geometry import Carton
from .stairs import layout


def _parse_set(items: list[str]) -> dict:
    out = {}
    for item in items:
        key, _, val = item.partition("=")
        out[key.strip()] = json.loads(val) if val.strip()[:1] in "[{-0123456789tfn" else val
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="milk_carton", description="Generate the milk carton schematics.")
    ap.add_argument("--config", help="JSON file of parameters (see config/default.json)")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="override one parameter, e.g. --set tilt_deg=45")
    ap.add_argument("--out", default="outputs", help="output directory (default: outputs)")
    ap.add_argument("--png", action="store_true", help="also write PNG copies (needs cairosvg)")
    ap.add_argument("--sweep", action="store_true", help="print the stair width x landing interval table")
    args = ap.parse_args(argv)

    cfg = Config.from_json(args.config) if args.config else Config()
    if args.set:
        cfg = cfg.replace(**_parse_set(args.set))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if cfg.form == "upright":
        from . import spout_figure, upright
        u = upright.Upright(cfg)
        files = {
            "upright_elevation.svg": upright.elevation(u),
            "upright_plan.svg": upright.plan(u),
            "spout.svg": spout_figure.render(u),
        }
        for name, content in files.items():
            (out / name).write_text(content)
        text = upright.report(u)
        (out / "report.md").write_text(text)
        (out / "config.used.json").write_text(json.dumps(cfg.to_dict(), indent=2) + "\n")
        if args.png:
            import cairosvg
            for name in files:
                cairosvg.svg2png(url=str(out / name), write_to=str(out / name.replace(".svg", ".png")), scale=1.5)
        print(text)
        print(f"Wrote {', '.join(files)} and report.md to {out}/")
        return 0 if not any(l == "fail" for l, _ in u.issues) else 1

    carton = Carton(cfg)
    lay = layout(cfg, carton)

    files = {
        "elevation.svg": elevation.render(cfg, carton, lay),
        "plan.svg": plan.render(cfg, carton, lay),
    }
    for name, content in files.items():
        (out / name).write_text(content)
    text = report.summary(cfg, carton, lay)
    if args.sweep:
        text += "\n## Stair sweep\n\n" + report.sweep_table(cfg)
    (out / "report.md").write_text(text)
    (out / "config.used.json").write_text(json.dumps(cfg.to_dict(), indent=2) + "\n")

    if args.png:
        import cairosvg
        for name in files:
            cairosvg.svg2png(url=str(out / name), write_to=str(out / name.replace(".svg", ".png")), scale=1.5)

    print(text)
    print(f"Wrote {', '.join(files)} and report.md to {out}/")
    return 0 if lay.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
