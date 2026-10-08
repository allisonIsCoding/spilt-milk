"""Design parameters for the BM Milk Carton schematic.

Every number the drawings and checks depend on lives here, in feet and
degrees. Override any of them from a JSON file (see config/default.json)
or on the command line (see `python -m milk_carton --help`).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path


@dataclass
class Config:
    # --- carton shell -----------------------------------------------------
    tilt_deg: float = 50.0          # tip angle from vertical
    height_ft: float = 40.0         # overall height, untilted
    width_ft: float = 18.9          # square footprint, both directions
    body_ft: float = 30.7           # straight-sided body
    roof_ft: float = 6.9            # gable rise above the body
    # fin height is whatever is left: height - body - roof
    ridge_inset_ft: float = 1.2     # fin starts this far in from the left wall
    beak_ft: float = 3.3            # how far the spout tip overhangs the right wall
    mouth_len_ft: float = 8.8       # length of the triangular opening along the ridge
    mouth_depth_ft: float = 3.6     # depth of the opening below the ridge top
    sink_ft: float = 2.8            # how far the base corner is sunk below grade

    # --- slide ------------------------------------------------------------
    slide_run_ft: float = 23.75     # horizontal reach from the mouth to the run-out
    slide_half_width_ft: float = 1.8
    slide_support_fracs: tuple = (0.22, 0.45, 0.62)  # where posts go along the run

    # --- form -------------------------------------------------------------
    form: str = "upright"           # "upright" (standing on its base) or "tipped" (tilt_deg over)

    # --- upright carton ------------------------------------------------------
    length_ft: float | None = 25.3  # along the ridge; the spout end is width_ft across (None = square)
    max_flight_run_ft: float = 10.0  # walls longer than this get a mid-wall landing
    wall_ft: float = 0.5            # wall thickness
    spiral_flights: int = 6         # flights in the spiral up to the eave deck
    eave_deck_ft: float = 24.0      # full floor just under the roof (headroom limit at the walls)
    spout_tip_out_ft: float = 4.8   # opened spout: how far the tip sticks out past the end wall
    spout_tip_above_ft: float = 1.4  # opened spout: tip height above the top of the fin
    spout_crease_back_ft: float = 2.0  # opened spout: where the side flap meets the lifted fin, back from the end wall
    roof_bend_side_back_ft: float = 4.5  # opened spout: where the roof bends reach the long sides, back from the end wall
    fin_lift_back_ft: float = 8.7   # opened spout: where the fin starts lifting, back from the end wall
    side_outlet_ft: float = 12.0    # slide: height of the tear in the spout-end wall (a landing there)
    side_slide_deg: float = 24.0    # slide: target grade

    # --- stairs -----------------------------------------------------------
    # "diagonal": flights run diagonally between landings on alternating sides (/\/\ from above)
    # "switchback": flights run straight across the width, stacked along the carton
    stair_layout: str = "diagonal"
    landing_size_ft: float = 6.0    # diagonal layout: landings are this size, square
    landing_x_ft: tuple | None = None  # diagonal layout: landing centres along X (None = search)
    door_x_ft: float | None = None  # diagonal layout: door centre along X (None = middle of the V)
    stair_width_ft: float = 4.5     # clear width between handrails
    landing_interval_ft: float = 4.0  # vertical gap between landings
    landing_depth_ft: float | None = None  # defaults to stair width
    flight_skew_ft: float = 0.0     # 0 = straight across; >0 = diagonal flights
    clearance_ft: float = 0.5       # minimum gap between stairs and carton surfaces
    headroom_ft: float = 6.7        # minimum clear height where flights stack in plan
    rail_height_ft: float = 3.5
    door_height_ft: float = 6.5
    comfort_pitch_deg: float = 35.0  # flights steeper than this get a warning
    max_pitch_deg: float = 38.0      # flights steeper than this fail

    # --- drawing ----------------------------------------------------------
    person_ft: float = 6.0

    @property
    def fin_ft(self) -> float:
        return self.height_ft - self.body_ft - self.roof_ft

    @property
    def landing_depth(self) -> float:
        return self.landing_depth_ft if self.landing_depth_ft is not None else self.stair_width_ft

    def validate(self) -> None:
        if self.fin_ft <= 0:
            raise ValueError("body_ft + roof_ft must be less than height_ft")
        if not 5 <= self.tilt_deg <= 80:
            raise ValueError("tilt_deg should be between 5 and 80")

    # --- io ---------------------------------------------------------------
    @classmethod
    def from_json(cls, path: str | Path) -> "Config":
        data = json.loads(Path(path).read_text())
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        known = {f.name for f in fields(cls)}
        unknown = set(data) - known
        if unknown:
            raise KeyError(f"Unknown config keys: {sorted(unknown)}")
        if "slide_support_fracs" in data:
            data = {**data, "slide_support_fracs": tuple(data["slide_support_fracs"])}
        if data.get("landing_x_ft") is not None:
            data = {**data, "landing_x_ft": tuple(data["landing_x_ft"])}
        cfg = cls(**data)
        cfg.validate()
        return cfg

    def to_dict(self) -> dict:
        return asdict(self)

    def replace(self, **changes) -> "Config":
        data = self.to_dict()
        data.update(changes)
        return Config.from_dict(data)
