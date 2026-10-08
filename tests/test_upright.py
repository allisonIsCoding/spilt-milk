import xml.etree.ElementTree as ET

import pytest

from milk_carton import spout_figure, upright
from milk_carton.config import Config


def model(**kw):
    return upright.Upright(Config(**kw))


def test_default_is_upright_with_short_roof():
    u = model()
    assert u.cfg.form == "upright"
    assert u.H == 40
    assert u.L / u.W == pytest.approx(6 / 4.5, rel=0.01)   # gallon carton footprint, 6 x 4.5 in
    assert 0.2 < (u.H - u.Hb) / u.H < 0.27          # roof + fin are the top ~23%


def test_spout_hinges_at_the_wall_top_and_tip_clears_the_fin():
    u = model()
    assert u.hinge == (u.L, u.Hb)
    assert u.tip_z > u.H
    assert u.tip_X > u.L
    assert u.lift_start[0] < u.crease_top[0] < u.L   # the fin lifts back from the end wall


def test_spiral_stairs_fit_under_the_eaves():
    u = model()
    assert u.pitch < u.cfg.comfort_pitch_deg
    assert u.roof_z(u.cfg.wall_ft) - u.deck_z >= u.cfg.headroom_ft
    assert u.lap_rise >= u.cfg.headroom_ft
    assert u.flights[-1][1] == pytest.approx(u.deck_z)
    assert u.max_rise < 6                            # a fall only goes as far as the next landing


def test_slide_leaves_from_a_landing_on_the_spout_end_wall():
    u = model()
    assert not any(lvl == "fail" for lvl, _ in u.issues)
    z, r, _ = u.outlet_landing()
    assert z == pytest.approx(u.cfg.side_outlet_ft, abs=0.3)
    assert r[1] == pytest.approx(u.L - u.cfg.wall_ft)
    line = u.side_slide()
    assert line[0] == (u.L, u.cfg.side_outlet_ft)
    assert u.side_max_deg <= 31


def test_outlet_off_a_landing_is_flagged():
    u = model(side_outlet_ft=17.0)
    assert any("not at a landing" in m for lvl, m in u.issues if lvl == "fail")


def test_all_upright_drawings_are_valid_svg():
    u = model()
    for svg in (upright.elevation(u), upright.plan(u), spout_figure.render(u)):
        assert ET.fromstring(svg).tag.endswith("svg")
