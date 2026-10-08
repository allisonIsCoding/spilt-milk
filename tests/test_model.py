import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from milk_carton import elevation, plan
from milk_carton.config import Config
from milk_carton.geometry import Carton
from milk_carton.stairs import layout

ROOT = Path(__file__).resolve().parents[1]


def test_default_json_matches_config_defaults():
    on_disk = json.loads((ROOT / "config" / "default.json").read_text())
    expected = Config().to_dict()
    expected["slide_support_fracs"] = list(expected["slide_support_fracs"])
    assert on_disk == expected


def test_surface_slopes_follow_tilt():
    c = Carton(Config(tilt_deg=50))
    assert c.floor_slope_deg == pytest.approx(40)
    assert c.panel_slope_deg == pytest.approx(50)
    c = Carton(Config(tilt_deg=45))
    assert c.floor_slope_deg == pytest.approx(45)


def test_key_dimensions_at_50_degrees():
    c = Carton(Config())
    x, z = c.spout_point()
    assert 19 < z < 20.5            # spout about 20 ft above grade
    assert 29 < x < 32              # and about 30 ft out from the base corner
    assert 33 < c.top_height() < 35.5
    lo, hi = c.v_range_at(0)
    assert hi - lo == pytest.approx(5.69, abs=0.05)   # interior is ~5.7 ft wide at grade


def test_slide_lands_at_grade_and_is_steep_but_finite():
    cfg = Config()
    c = Carton(cfg)
    _, z_end = c.slide_end()
    assert z_end == pytest.approx(cfg.slide_half_width_ft)
    assert 55 < c.slide_max_slope_deg() < 75


def test_default_stairs_pass_every_check():
    lay = layout(Config())
    assert lay.ok and not lay.issues
    assert len(lay.flights) == 5
    assert lay.max_fall_ft == pytest.approx(4.0)
    assert lay.max_pitch_deg < 35


def test_wide_stairs_do_not_fit_at_grade():
    # the V is only ~5.7 ft wide at grade, so anything over ~4.7 ft cannot start there
    for w in (5.0, 5.5, 6.0):
        lay = layout(Config(stair_width_ft=w))
        assert not lay.ok
        assert any("V is only" in m for _, m in lay.issues)


def test_pitch_gets_steeper_as_stairs_widen():
    narrow = layout(Config(stair_width_ft=4.0, landing_interval_ft=5.0)).max_pitch_deg
    wide = layout(Config(stair_width_ft=4.5, landing_interval_ft=5.0)).max_pitch_deg
    assert wide > narrow


def test_diagonal_flights_run_into_the_floor():
    # Each skewed flight advances along the carton faster than the 40 deg floor allows.
    lay = layout(Config(flight_skew_ft=1.0))
    assert not lay.ok
    assert any("surface" in m for _, m in lay.issues)


def test_renderers_emit_valid_svg():
    cfg = Config()
    for svg in (elevation.render(cfg), plan.render(cfg)):
        root = ET.fromstring(svg)
        assert root.tag.endswith("svg")


def test_unknown_config_key_is_rejected():
    with pytest.raises(KeyError):
        Config.from_dict({"stair_wdith_ft": 5})


def test_floor_clearance_is_never_negative_for_default():
    lay = layout(Config())
    assert lay.min_clearance_ft >= Config().clearance_ft - 1e-6
    assert math.isfinite(lay.min_clearance_ft)
